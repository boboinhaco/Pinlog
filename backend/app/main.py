from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.errors import NextoError, nexto_error_handler, generic_error_handler
from .db.bootstrap import ensure_schema
from .api import auth, shares, jobs, items, calendar, places


# 시작할 때 DB 스키마 준비 (새 DB면 테이블 생성)
@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_schema()
    yield


app = FastAPI(title="Pinlog API", version="3.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(NextoError, nexto_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

for r in (auth, shares, jobs, items, calendar, places): app.include_router(r.router)


# AC-10 공개 URL health check
@app.get("/health")
async def health():
    return {"ok": True, "demo_mode": settings.demo_mode}


# 배포 시 프론트 빌드 결과를 같은 서버에서 제공 (STATIC_DIR): 파일이 있으면 파일, 나머지 경로는 SPA index.html
static = Path(settings.static_dir) if settings.static_dir else None
if static and static.is_dir():
    app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str):
        if path.startswith("api/"): raise NextoError("NOT_FOUND", "없는 API 경로예요.", status=404)
        file = static / path
        return FileResponse(file if path and file.is_file() else static / "index.html")
