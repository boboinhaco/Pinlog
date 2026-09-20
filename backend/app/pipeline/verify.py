import json
from ..schemas import ExtractionPayload, SourceDoc, VerificationPayload, FieldResult
from ..services.grading import grade
from ..services import llm

FIELDS =("title", "target", "eligibility", "apply_period", "event_period", "benefit_amount", "location", "requirements")
OFFICIAL_TYPES = ("OFFICIAL_GOV", "OFFICIAL_PUBLIC", "OFFICIAL_FINANCE", "OFFICIAL_ORGANIZER")


# 기간 룰 비교: SNS ⊂ 공식 → REFINED, 교집합 없음 → CONFLICT
def compare_period(sns: dict, official: dict) -> str:
    if not sns.get("end") or not official.get("end"): return "AMBIGUOUS"
    if sns == official: return "VERIFIED"
    if official.get("start", "") <= sns.get("start", official.get("start", "")) and sns["end"] <= official["end"]: return "REFINED"
    return "CONFLICT"


# 연령 구간 비교
def compare_age(sns: dict, official: dict) -> str:
    keys = ("age_min", "age_max")
    if any(sns.get(k) is None or official.get(k) is None for k in keys): return "AMBIGUOUS"
    if all(sns[k] == official[k] for k in keys): return "VERIFIED"
    if official["age_min"] <= sns["age_min"] and sns["age_max"] <= official["age_max"]: return "REFINED"
    return "CONFLICT"


PROMPT = """너는 SNS 정보를 공식 출처와 대조하는 검증기야. 출처 원문에 있는 내용만 근거로 쓰고, 없으면 지어내지 마.

[SNS에서 추출한 값]
{sns}

[검색된 출처] (index, 도메인 분류, 제목, URL, 원문 일부)
{sources}

JSON 하나만 출력:
{{
  "primary_source_index": SNS가 말하는 바로 그 사업·상품·행사를 다루는 가장 공식적인 출처 index 또는 null,
  "is_official": 그 출처가 기관·은행·주최측이 직접 운영하는 공식 페이지면 true,
  "official_summary": "공식 출처 기준으로 무엇인지 2~3문장 요약" 또는 null,
  "official": {{
    "title": "공식 명칭|null",
    "target": {{"text": "...", "age_min": 정수|null, "age_max": 정수|null, "region": "...|null"}} 또는 null,
    "eligibility": ["공식 자격요건"],
    "apply_period": {{"start": "YYYY-MM-DD|null", "end": "YYYY-MM-DD|null", "status": "exact|ambiguous|unknown"}},
    "event_period": {{"start": "YYYY-MM-DD|null", "end": "YYYY-MM-DD|null", "status": "exact|ambiguous|unknown"}} 또는 null,
    "benefit_amount": {{"text": "..."}} 또는 null,
    "location": {{"name": "...", "address": "...|null"}} 또는 null,
    "requirements": ["공식 제출서류"]
  }},
  "fields": [
    {{"field": "{field_names} 중 하나", "sns_value": "SNS 값을 사람이 읽을 문장으로|null", "official_value": "공식 값을 사람이 읽을 문장으로|null",
      "status": "VERIFIED|REFINED|CONFLICT|ADDED|AMBIGUOUS|UNVERIFIED", "evidence": "공식 출처 원문 인용(짧게)|null"}}
  ]
}}

중요: SNS 게시물이 특정 이름의 사업·상품·행사를 가리키지 않거나(예: "추천 상품 모음"처럼 대상이 불분명), 출처가 다른 대상(다른 은행 상품, 다른 연도 행사 등)을 다루면
primary_source_index는 null, official은 빈 객체, fields의 status는 모두 UNVERIFIED로 둬. 비슷해 보인다고 연결하지 마.

status 기준:
- VERIFIED: SNS 값과 공식 값이 같음
- REFINED: SNS가 대략적이고 공식 값이 더 구체적임 (모순 없음)
- CONFLICT: SNS 값과 공식 값이 다름 (나이·금액·날짜 불일치 등)
- ADDED: SNS엔 없고 공식 출처에만 있음
- AMBIGUOUS: 공식 출처가 있으나 이 항목을 확정할 수 없음
- UNVERIFIED: 공식 출처에서 이 항목을 찾지 못함
SNS나 공식 중 한쪽에라도 값이 있는 항목만 fields에 넣어.
"""


def _sources_block(sources: list[SourceDoc]) -> str:
    return "\n\n".join(f"[{i}] {s.domain_type} | {s.title} | {s.url}\n{s.excerpt[:3000]}" for i, s in enumerate(sources))


# A4: LLM 근거 판정 + 기간 룰 비교, 등급은 규칙으로 산정
async def run(ex: ExtractionPayload, sources: list[SourceDoc]) -> VerificationPayload:
    # SNS에 대조할 구체적 사실이 없으면(모음글·홍보 문구뿐) 비슷한 출처와 억지로 연결하지 않음
    if not sources or not has_facts(ex):
        fields = [FieldResult(field=f, sns_value=_display(getattr(ex, f, None)), status="UNVERIFIED") for f in FIELDS if _display(getattr(ex, f, None))]
        return VerificationPayload(fields=fields, overall_grade="UNVERIFIED")
    sns = ex.model_dump(include=set(FIELDS) | {"summary", "organization", "category", "key_points"})
    data = await llm.generate_json(PROMPT.format(sns=json.dumps(sns, ensure_ascii=False), sources=_sources_block(sources), field_names="|".join(FIELDS)))
    idx = data.get("primary_source_index")
    primary = sources[idx] if isinstance(idx, int) and 0 <= idx < len(sources) else None
    if primary and data.get("is_official") and primary.domain_type in ("UNKNOWN",): primary.domain_type = "OFFICIAL_ORGANIZER"
    official = data.get("official") or {}
    fields = []
    for f in data.get("fields") or []:
        if f.get("field") not in FIELDS or f.get("status") not in ("VERIFIED", "REFINED", "CONFLICT", "ADDED", "AMBIGUOUS", "UNVERIFIED"): continue
        fields.append(FieldResult(**{k: f.get(k) for k in ("field", "sns_value", "official_value", "status", "evidence")}))
    if not primary:
        for f in fields: f.status, f.official_value, f.evidence = "UNVERIFIED", None, None
    # 날짜는 LLM 판단보다 룰 우선
    sp, op = ex.apply_period.model_dump(), official.get("apply_period") or {}
    if primary and sp.get("end") and op.get("end"):
        for f in fields:
            if f.field == "apply_period": f.status = compare_period(sp, op)
    has_official = bool(primary) and primary.domain_type in OFFICIAL_TYPES
    return VerificationPayload(primary_source=primary, fields=fields, overall_grade=grade(has_official, fields),
                               official_summary=data.get("official_summary") if primary else None, official=official if primary else {})


def has_facts(ex: ExtractionPayload) -> bool:
    period = lambda p: bool(p and (p.start or p.end))
    return any([ex.target, ex.eligibility, ex.benefit_amount, ex.location, ex.requirements, period(ex.apply_period), period(ex.event_period), ex.events])


# 표시용 문자열 (검증 없이 SNS 값만 보여줄 때)
def _display(v) -> str | None:
    if v is None or v == [] or v == {}: return None
    if hasattr(v, "model_dump"): v = v.model_dump()
    if isinstance(v, list): return ", ".join(map(str, v))
    if isinstance(v, dict):
        if v.get("text"): return v["text"]
        if "start" in v or "end" in v: return " ~ ".join(x for x in (v.get("start"), v.get("end")) if x) or None
        if v.get("name"): return " ".join(x for x in (v.get("name"), v.get("address")) if x)
        return None
    return str(v)
