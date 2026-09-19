from datetime import date
from pathlib import Path
from ..schemas import ExtractionPayload
from ..services import llm
from . import understand as understand_stage

PROMPT = """너는 SNS 게시물에서 '다음 행동'에 필요한 정보를 뽑는 추출기야. 오늘은 {today}.
아래 게시물(캡션/본문)과 첨부 이미지를 보고 JSON 하나만 출력해. 게시물에 없는 정보는 지어내지 말고 null 또는 빈 배열로 둬.

category: POLICY_HOUSING(청년 주거·월세·임대) | POLICY_JOB(취업·일자리) | POLICY_LIVING(생활 지원) | SUBSCRIPTION(주택청약) | FINANCE(예적금·금융상품·계좌) | EVENT(축제·행사·전시·공연·팝업) | RECRUIT(모집) | CONTEST(공모전) | OTHER

출력 형식:
{{
  "title": "대표 이름 (사업명/상품명/행사명)",
  "category": "...",
  "summary": "이 게시물이 알려주는 내용을 2~3문장으로 요약",
  "organization": "주관 기관/은행/주최 또는 null",
  "benefit_amount": {{"text": "혜택을 게시물 표현 그대로", "value": 원 단위 정수 또는 null, "period": "MONTHLY|ONCE|YEARLY|null"}} 또는 null,
  "target": {{"text": "대상 한 줄 요약", "age_min": 정수|null, "age_max": 정수|null, "region": "지역|null"}} 또는 null,
  "eligibility": ["자격요건 (소득·재직·무주택 등) 하나씩"],
  "apply_period": {{"start": "YYYY-MM-DD|null", "end": "YYYY-MM-DD|null", "status": "exact|ambiguous|unknown"}},
  "event_period": {{"start": "YYYY-MM-DD|null", "end": "YYYY-MM-DD|null", "status": "exact|ambiguous|unknown"}} 또는 null,
  "location": {{"name": "장소명", "address": "주소|null"}} 또는 null,
  "requirements": ["준비 서류/준비물"],
  "key_points": ["위 항목에 안 들어가는 유용한 정보 요약 (금리, 우대조건, 유의사항, 상품 목록 등) 최대 6개"],
  "raw_evidence": ["근거가 된 원문 구절 최대 5개"],
  "events": [{{"title": "...", "event_period": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "status": "exact"}}, "location": {{"name": "...", "address": "...|null"}}}}],
  "notice": "대상·자격·기간 같은 핵심 정보를 이 내용만으로 알 수 없으면 그 이유를 사용자에게 한 문장으로 (예: 상세 내용이 뒤쪽 이미지 슬라이드에 있어 보이지 않아요) 아니면 null"
}}

규칙:
- 날짜는 연도가 없으면 오늘 기준 가장 가까운 미래로 채우고 status를 "ambiguous"로. "9월까지"처럼 말일을 추정했으면 역시 "ambiguous".
- 마감만 있으면 apply_period.end만 채워.
- 여러 상품·정책을 모아 소개하는 글이면 title은 모음 제목으로, 개별 이름·조건은 key_points에 적어.
- events는 게시물 하나에 서로 다른 행사/일정이 여러 개일 때만 각각 넣어. 하나뿐이면 빈 배열로 두고 event_period를 채워.

게시물 링크: {url}
게시물 내용:
{content}
"""


def _load_local(path: str) -> tuple[str, bytes] | None:
    p = Path(path)
    return ("image/jpeg", p.read_bytes()) if p.exists() else None


# A2: LLM 구조화 추출 (업로드 이미지 + 링크 대표 이미지)
async def run(understanding: dict) -> ExtractionPayload:
    link = understanding.get("link") or {}
    images = [img for img in (_load_local(p) for p in understanding.get("image_paths", [])) if img]
    og = await understand_stage.download_image(link.get("image_url"))
    if og: images.append(og)
    content = understanding.get("summary") or ""
    if not content.strip() and not images:
        raise llm.LLMError(link.get("error") or "링크에서 읽을 수 있는 내용이 없어요. 캡션 텍스트나 스크린샷을 함께 넣어주세요.")
    data = await llm.generate_json(PROMPT.format(today=date.today().isoformat(), url=understanding.get("url") or "-", content=content or "(텍스트 없음, 이미지 참고)"), images[:5])
    data["image_url"] = link.get("image_url")
    if not data.get("event_period") or not (data["event_period"] or {}).get("start"): data["event_period"] = None
    return ExtractionPayload(**{k: v for k, v in data.items() if v is not None or k in ("event_period",)})
