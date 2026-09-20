import hashlib
from datetime import date
from urllib.parse import urlparse
import httpx
from ..core.config import settings
from ..schemas import ExtractionPayload, SourceDoc

# 명세서 7.1 도메인 화이트리스트 (+ 은행·청년정책 포털)
PUBLIC = ("lh.or.kr", "i-sh.co.kr", "applyhome.co.kr", "myhome.go.kr", "youthcenter.go.kr", "youth.seoul.go.kr", "kinfa.or.kr", "hf.go.kr", "khug.or.kr", "work24.go.kr")
FINANCE = ("fsc.go.kr", "fss.or.kr", "kbstar.com", "shinhan.com", "wooribank.com", "hanabank.com", "ibk.co.kr", "nhbank.com", "kakaobank.com",
           "tossbank.com", "kbanknow.com", "busanbank.co.kr", "dgb.co.kr", "knbank.co.kr", "kjbank.com", "jbbank.co.kr", "sc.co.kr", "citibank.co.kr", "epostbank.go.kr", "kfcc.co.kr", "cu.co.kr")
SECONDARY = ("news", "blog", "namu.wiki", "tistory.com", "brunch.co.kr", "cafe.naver.com", "youtube.com", "instagram.com", "facebook.com", "wikipedia.org")


def classify_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if any(host.endswith(d) for d in PUBLIC): return "OFFICIAL_PUBLIC"
    if any(host.endswith(d) for d in FINANCE): return "OFFICIAL_FINANCE"
    if host.endswith(".go.kr"): return "OFFICIAL_GOV"
    if any(s in host for s in SECONDARY): return "SECONDARY"
    return "UNKNOWN"


def url_hash(url: str) -> str:
    return hashlib.sha256(url.split("#")[0].rstrip("/").encode()).hexdigest()


# 검색 질의: 이름 + 기관 + 연도, 카테고리별 공고/상품/행사 키워드
SUFFIX = {"FINANCE": "가입 조건 공식", "EVENT": "공식 홈페이지 일정", "POLICY_HOUSING": "공고", "SUBSCRIPTION": "모집공고"}


def build_queries(ex: ExtractionPayload, year: int | None = None) -> list[str]:
    year = year or date.today().year
    parts = [ex.title, ex.organization or "", str(year)]
    return [" ".join(p for p in parts if p), f"{ex.title} {SUFFIX.get(ex.category, '공고')}"]


# 순위: 공식 도메인 우선, 주최측(UNKNOWN)은 2차 자료보다 앞
RANK = {"OFFICIAL_GOV": 0, "OFFICIAL_PUBLIC": 1, "OFFICIAL_FINANCE": 2, "OFFICIAL_ORGANIZER": 3, "UNKNOWN": 4, "SECONDARY": 5}


# Tavily 검색 (공식 출처는 본문까지, 상품 확인은 가볍게)
async def tavily(query: str, *, max_results: int = 8, depth: str = "advanced", raw: bool = True) -> list[dict]:
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {settings.web_search_api_key}"},
                                json={"query": query, "max_results": max_results, "search_depth": depth, "include_raw_content": raw, "country": "south korea"})
    res.raise_for_status()
    return res.json().get("results", [])


# A3: 검색 API → 화이트리스트 정렬 → 본문 확보 → Top 3
async def run(ex: ExtractionPayload) -> list[SourceDoc]:
    if not settings.web_search_api_key: return []
    seen, candidates = set(), []
    for q in build_queries(ex):
        try:
            results = await tavily(q)
        except Exception:
            continue
        for r in results:
            h = url_hash(r["url"])
            if h in seen: continue
            seen.add(h)
            body = (r.get("raw_content") or r.get("content") or "").strip()
            candidates.append(SourceDoc(url=r["url"], domain_type=classify_domain(r["url"]), title=r.get("title") or "", excerpt=body[:4000]))
    candidates.sort(key=lambda s: RANK[s.domain_type])
    top = [s for s in candidates if s.excerpt][:3]
    for i, s in enumerate(top): s.rank = i
    return top
