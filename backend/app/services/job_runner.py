import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from ..db.session import SessionLocal
from ..db.models import AnalysisJob, ContentShare, MediaAsset, Extraction, SourceDocument, VerificationResult
from ..pipeline import understand, extract, normalize, search, verify, products
from ..pipeline.search import url_hash
from ..schemas import ExtractionPayload, SourceDoc, VerificationPayload, ProductCandidate
from ..core.config import settings
from . import sse, demo, llm

MESSAGES ={"UNDERSTAND": "콘텐츠를 읽는 중", "EXTRACT": "핵심 정보를 추출하는 중", "NORMALIZE": "날짜와 금액을 정리하는 중",
            "SEARCH": "공식 출처를 찾는 중", "VERIFY": "공식 정보와 비교하는 중"}


# 단계 진행 저장 + SSE 발행
async def _progress(db, job: AnalysisJob, stage: str, result=None, message: str | None = None):
    job.stage = stage
    if result is not None: job.stage_results = {**job.stage_results, stage: result}
    await db.commit()
    await sse.publish(str(job.job_id), "progress", {"job_id": str(job.job_id), "stage": stage, "message": message or MESSAGES.get(stage, "")})


# Job 실행, 실패한 단계부터 재시도 가능 (stage_results 재사용)
async def run_job(job_id: str):
    async with SessionLocal() as db:
        job = await db.get(AnalysisJob, job_id)
        share = await db.get(ContentShare, job.share_id)
        assets = (await db.execute(select(MediaAsset).where(MediaAsset.share_id == share.share_id).order_by(MediaAsset.asset_order))).scalars().all()
        job.status, job.started_at = "RUNNING", datetime.now(timezone.utc)
        await db.commit()
        done = job.stage_results or {}
        try:
            async with asyncio.timeout(settings.job_hard_timeout_sec):
                fixture = demo.load_fixture(f"{share.text or ''} {share.original_url or ''}")
                if "UNDERSTAND" not in done:
                    await _progress(db, job, "UNDERSTAND")
                    done["UNDERSTAND"] = {"summary": share.text or "", "fixture": True} if fixture else \
                        await understand.run(share.text or "", [a.storage_key for a in assets], share.original_url)
                    await _progress(db, job, "UNDERSTAND", done["UNDERSTAND"])
                if "EXTRACT" not in done:
                    await _progress(db, job, "EXTRACT")
                    ex = ExtractionPayload(**fixture["extraction"]) if fixture else await extract.run(done["UNDERSTAND"])
                    if not ex.image_url and share.original_url: ex.image_url = (done["UNDERSTAND"].get("link") or {}).get("image_url")
                    await _progress(db, job, "EXTRACT", ex.model_dump())
                    done["EXTRACT"] = ex.model_dump()
                ex = ExtractionPayload(**done["EXTRACT"])
                if "NORMALIZE" not in done:
                    await _progress(db, job, "NORMALIZE")
                    ex = await normalize.run(ex)
                    await _progress(db, job, "NORMALIZE", ex.model_dump()); done["NORMALIZE"] = ex.model_dump()
                ex = ExtractionPayload(**done["NORMALIZE"])
                if "SEARCH" not in done:
                    await _progress(db, job, "SEARCH")
                    # 물건 소개 글은 공식 공고가 없으니 출처 검색은 건너뜀
                    sources = [SourceDoc(**s) for s in fixture["sources"]] if fixture else ([] if ex.category == "PRODUCT" else await search.run(ex))
                    await _progress(db, job, "SEARCH", [s.model_dump() for s in sources]); done["SEARCH"] = [s.model_dump() for s in sources]
                sources = [SourceDoc(**s) for s in done["SEARCH"]]
                # 사진·글에서 나온 제품은 인터넷 검색으로 상품명·구매처 확인 (예시 데이터는 이미 확인된 값)
                if "PRODUCTS" not in done:
                    if ex.products and not fixture: await _progress(db, job, "SEARCH", message="사진 속 상품을 찾는 중")
                    found = await products.run(ex) if ex.products and not fixture else ex.products
                    await _progress(db, job, "SEARCH", None); done["PRODUCTS"] = [p.model_dump() for p in found]
                    job.stage_results = {**job.stage_results, "PRODUCTS": done["PRODUCTS"]}; await db.commit()
                ex.products = [ProductCandidate(**p) for p in done["PRODUCTS"]]
                if "VERIFY" not in done:
                    await _progress(db, job, "VERIFY")
                    ver = VerificationPayload(**fixture["verification"]) if fixture else await verify.run(ex, sources)
                    await _progress(db, job, "VERIFY", ver.model_dump()); done["VERIFY"] = ver.model_dump()
                ver = VerificationPayload(**done["VERIFY"])

                # 최종 결과 영속화
                extraction = Extraction(share_id=share.share_id, model_name="fixture" if fixture else (llm.last_model or settings.llm_model), payload_json={**ex.model_dump(), "demo": bool(fixture)})
                db.add(extraction); await db.flush()
                for s in sources:
                    db.add(SourceDocument(extraction_id=extraction.extraction_id, url=s.url, url_hash=url_hash(s.url), domain_type=s.domain_type,
                                          title=s.title, excerpt=s.excerpt, rank=s.rank))
                db.add(VerificationResult(extraction_id=extraction.extraction_id, overall_grade=ver.overall_grade,
                                          fields_json={"fields": [f.model_dump() for f in ver.fields], "official_summary": ver.official_summary, "official": ver.official,
                                                       "primary_source_url": ver.primary_source.url if ver.primary_source else None}))
                job.status, job.stage, job.finished_at = "COMPLETED", "DONE", datetime.now(timezone.utc)
                await db.commit()
                await sse.publish(str(job.job_id), "completed", {"job_id": str(job.job_id), "share_id": str(share.share_id), "overall_grade": ver.overall_grade})
        except TimeoutError:
            await _fail(db, job, "TIMEOUT", "처리 시간이 초과됐어요. 다시 시도해 주세요.", True)
        except llm.LLMError as e:
            await _fail(db, job, "LLM_ERROR", str(e), True)
        except Exception as e:
            await _fail(db, job, "SCHEMA_INVALID" if "validation" in str(e).lower() else "INTERNAL", f"분석 중 오류가 났어요: {e}", True)


async def _fail(db, job: AnalysisJob, code: str, message: str, retryable: bool):
    job.status, job.error_code, job.error_message, job.finished_at = "FAILED", code, message, datetime.now(timezone.utc)
    await db.commit()
    await sse.publish(str(job.job_id), "failed", {"job_id": str(job.job_id), "code": code, "stage": job.stage, "message": message, "retryable": retryable})
