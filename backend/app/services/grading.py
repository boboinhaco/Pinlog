from ..schemas import FieldResult

CORE = {"title", "apply_period", "benefit_amount", "target", "event_period", "location"}


# 명세서 6.3: HIGH / REVIEW / UNVERIFIED 3단계
def grade(has_official_source: bool, fields: list[FieldResult]) -> str:
    if not has_official_source: return "UNVERIFIED"
    statuses = {f.field: f.status for f in fields}
    present = [f for f in CORE if f in statuses]
    grounded = sum(1 for f in present if statuses[f] in ("VERIFIED", "REFINED", "ADDED"))
    has_issue = any(s in ("CONFLICT", "AMBIGUOUS") for s in statuses.values())
    # 핵심 항목 3개 이상(항목이 적으면 전부)이 공식 근거로 확인되면 HIGH
    return "HIGH" if present and grounded >= min(3, len(present)) and not has_issue else "REVIEW"
