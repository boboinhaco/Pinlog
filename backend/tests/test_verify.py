from app.schemas import ExtractionPayload, SourceDoc
from app.pipeline import verify


# 모음글처럼 구체적 사실이 없으면 비슷한 출처가 있어도 공식 근거로 연결하지 않음 (LLM 호출 없음)
async def test_no_facts_stays_unverified(monkeypatch):
    async def boom(*a, **k): raise AssertionError("LLM should not be called")
    monkeypatch.setattr(verify.llm, "generate_json", boom)
    ex = ExtractionPayload(title="예적금 추천 모음", category="FINANCE", summary="추천 상품 모음")
    src = [SourceDoc(url="https://www.tossbank.com/articles/x", domain_type="OFFICIAL_FINANCE", title="파킹통장", excerpt="금리 3%")]
    ver = await verify.run(ex, src)
    assert ver.overall_grade == "UNVERIFIED" and ver.primary_source is None
    assert all(f.status == "UNVERIFIED" for f in ver.fields)


def test_has_facts():
    assert not verify.has_facts(ExtractionPayload(title="모음"))
    assert verify.has_facts(ExtractionPayload(title="청년월세", apply_period={"end": "2026-05-29", "status": "exact"}))
