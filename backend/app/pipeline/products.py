import asyncio
from urllib.parse import quote, urlparse
from ..core.config import settings
from ..schemas import ExtractionPayload, ProductCandidate, ProductLink
from ..services import llm
from .search import tavily, SECONDARY

# 주요 쇼핑몰 → '구매처'로 표시
SHOPS = ("smartstore.naver.com", "brand.naver.com", "shopping.naver.com", "coupang.com", "musinsa.com", "oliveyoung.co.kr", "29cm.co.kr", "kream.co.kr",
         "ssg.com", "lotteon.com", "gmarket.co.kr", "11st.co.kr", "auction.co.kr", "kurly.com", "ohou.se", "wconcept.co.kr", "zigzag.kr", "a-bly.com",
         "gift.kakao.com", "amazon.com", "aliexpress.com", "danawa.com", "enuri.com")
NAVER_SHOPPING = "https://search.shopping.naver.com/search/all?query={q}"
KIND_ORDER = {"official": 0, "shop": 1, "other": 2, "search": 3}

PROMPT = """너는 SNS 사진과 글에서 뽑은 제품 후보를 인터넷 검색 결과와 대조해 실제 상품명을 확인하는 도우미야.
후보마다 검색 결과 중 같은 제품을 다루는 것이 있으면 그 상품명을 matched_name에 적고, 없으면 null로 둬. 비슷해 보인다고 확정하지 마.
JSON 하나만 출력:
{{"products": [{{"index": 후보 번호, "matched_name": "검색으로 확인한 정확한 상품명|null", "brand": "브랜드|null",
  "confidence": "high|similar", "note": "한 문장 근거 또는 주의점 (사용자에게 보여주는 문장이라 '~요'체로)",
  "official_index": 브랜드 공식 사이트인 검색 결과 번호|null, "link_indexes": [관련 검색 결과 번호 최대 3개, 공식 사이트·구매처 우선]}}]}}

confidence 기준:
- high: 브랜드와 모델명이 사진·글의 글자와 검색 결과에서 모두 확인됨
- similar: 종류·생김새만 비슷하고 정확한 모델은 확정 못 함 (matched_name은 null)

후보:
{candidates}

검색 결과:
{results}
"""


def link_kind(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if any(host == s or host.endswith("." + s) for s in SHOPS): return "shop"
    return "other"


# 블로그·커뮤니티·영상 같은 2차 자료는 구매 링크로 쓰지 않음
def _secondary(url: str) -> bool:
    return any(s in urlparse(url).netloc.lower() for s in SECONDARY)


# 이름에 브랜드가 이미 들어 있으면 중복해서 붙이지 않음
def _with_brand(brand: str | None, name: str) -> str:
    return name if not brand or brand.lower().replace(" ", "") in name.lower().replace(" ", "") else f"{brand} {name}"


def _query(p: ProductCandidate) -> str:
    text = p.visible_text if p.visible_text and p.visible_text.lower() not in p.name.lower() else None
    kind = p.kind if p.kind and p.kind not in p.name else None
    return " ".join(x for x in (_with_brand(p.brand, p.name), text, kind) if x)


# 항상 붙는 쇼핑 검색 링크 (검색 API가 없어도 찾아볼 수 있게)
def _search_link(p: ProductCandidate) -> ProductLink:
    q = _with_brand(p.brand, p.matched_name or p.name)
    return ProductLink(url=NAVER_SHOPPING.format(q=quote(q)), title=f"네이버쇼핑에서 '{q}' 검색", kind="search")


async def _lookup(p: ProductCandidate) -> list[dict]:
    try:
        return await tavily(_query(p), max_results=6, depth="basic", raw=False)
    except Exception:
        return []


def _cand_line(i: int, p: ProductCandidate) -> str:
    bits = [f"이름: {p.name}", f"브랜드: {p.brand or '-'}", f"종류: {p.kind or '-'}", f"특징: {p.features or '-'}",
            f"사진 속 글자: {p.visible_text or '-'}", f"게시물 가격: {p.price_text or '-'}"]
    return f"[{i}] " + ", ".join(bits)


# 후보별 검색 → LLM 대조 → 링크 정리. 실패해도 job은 계속 (후보 + 쇼핑 검색 링크만)
async def run(ex: ExtractionPayload) -> list[ProductCandidate]:
    cands = [p.model_copy(update={"links": []}) for p in ex.products[:6]]
    if not cands: return []
    if settings.web_search_api_key and settings.llm_api_key:
        found = await asyncio.gather(*(_lookup(p) for p in cands))
        flat = [(i, r) for i, rs in enumerate(found) for r in rs if r.get("url")]
        if flat:
            results = "\n".join(f"[{n}] (후보 {i}) {r.get('title', '')} | {r['url']}\n    {(r.get('content') or '')[:300]}" for n, (i, r) in enumerate(flat))
            try:
                data = await llm.generate_json(PROMPT.format(candidates="\n".join(_cand_line(i, p) for i, p in enumerate(cands)), results=results))
                _apply(cands, data.get("products") or [], flat)
            except llm.LLMError:
                pass
    for p in cands:
        p.links = sorted([*p.links, _search_link(p)], key=lambda l: KIND_ORDER.get(l.kind, 9))
    return cands


def _apply(cands: list[ProductCandidate], rows: list[dict], flat: list[tuple[int, dict]]):
    for row in rows:
        i = row.get("index")
        if not isinstance(i, int) or not 0 <= i < len(cands): continue
        p = cands[i]
        p.matched_name = (row.get("matched_name") or "").strip() or None
        p.brand = row.get("brand") or p.brand
        p.confidence = "high" if p.matched_name and row.get("confidence") == "high" else "similar"
        p.note = (row.get("note") or "").strip() or None
        official = row.get("official_index")
        seen, links = set(), []
        for n in row.get("link_indexes") or []:
            if not isinstance(n, int) or not 0 <= n < len(flat): continue
            r = flat[n][1]
            if r["url"] in seen or _secondary(r["url"]): continue
            seen.add(r["url"])
            links.append(ProductLink(url=r["url"], title=r.get("title") or "", kind="official" if n == official else link_kind(r["url"])))
        p.links = links[:3]
