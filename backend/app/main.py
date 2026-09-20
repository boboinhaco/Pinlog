from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.errors import NextoError, nexto_error_handler, generic_error_handler
from .api import auth, shares, jobs, items, calendar, places

app = FastAPI(title="Pinlog API", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(NextoError, nexto_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

for r in (auth, shares, jobs, items, calendar, places): app.include_router(r.router)


# AC-10 공개 URL health check
@app.get("/health")
async def health():
    return {"ok": True, "demo_mode": settings.demo_mode}
