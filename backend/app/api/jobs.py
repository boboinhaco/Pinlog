import asyncio, json
from fastapi import APIRouter, BackgroundTasks, Depends
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db
from ..db.models import AnalysisJob
from ..core.errors import NextoError, ok
from ..services import sse
from ..services.job_runner import run_job, MESSAGES

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _view(job: AnalysisJob):
    return {"job_id": str(job.job_id), "share_id": str(job.share_id), "status": job.status, "stage": job.stage,
            "error": {"code": job.error_code, "stage": job.stage, "message": job.error_message, "retryable": True} if job.error_code else None}


# polling용 상태 조회
@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(AnalysisJob, job_id)
    if not job: raise NextoError("NOT_FOUND", "job을 찾을 수 없어요.", status=404)
    return ok(_view(job))


# SSE 스트림, 이미 끝난 job이면 즉시 종료 이벤트
@router.get("/{job_id}/stream")
async def stream(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(AnalysisJob, job_id)
    if not job: raise NextoError("NOT_FOUND", "job을 찾을 수 없어요.", status=404)

    async def gen():
        if job.status in ("COMPLETED", "FAILED"):
            yield {"event": "completed" if job.status == "COMPLETED" else "failed", "data": json.dumps(_view(job), ensure_ascii=False)}; return
        q = sse.subscribe(job_id)
        # 접속 전에 지나간 단계는 못 받으니 현재 단계를 먼저 보내줌
        if job.stage and job.stage != "DONE":
            yield {"event": "progress", "data": json.dumps({"job_id": job_id, "stage": job.stage, "message": MESSAGES.get(job.stage, "")}, ensure_ascii=False)}
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15)
                    yield {"event": msg["event"], "data": json.dumps(msg["data"], ensure_ascii=False)}
                    if msg["event"] != "progress": return
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
        finally:
            sse.unsubscribe(job_id, q)
    return EventSourceResponse(gen())


# 실패한 단계부터 재실행 (stage_results 보존)
@router.post("/{job_id}/retry")
async def retry(job_id: str, bg: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    job = await db.get(AnalysisJob, job_id)
    if not job: raise NextoError("NOT_FOUND", "job을 찾을 수 없어요.", status=404)
    job.status, job.error_code, job.error_message = "QUEUED", None, None
    await db.commit()
    bg.add_task(run_job, job_id)
    return ok(_view(job))
