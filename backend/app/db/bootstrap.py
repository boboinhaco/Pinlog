from pathlib import Path
import asyncpg
from ..core.config import settings
from .session import split_dsn

DB_DIR = Path(__file__).resolve().parents[2] / "db"


# 서버 시작 시 스키마 준비: 테이블이 없으면 init.sql, 그다음 migrations/*.sql (IF NOT EXISTS라 반복 실행해도 안전)
async def ensure_schema():
    url, ssl = split_dsn(settings.database_url)
    conn = await asyncpg.connect(url.replace("postgresql+asyncpg://", "postgresql://", 1), ssl="require" if ssl else None)
    try:
        if not await conn.fetchval("SELECT to_regclass('public.users') IS NOT NULL"):
            await conn.execute((DB_DIR / "init.sql").read_text(encoding="utf-8"))
        for f in sorted((DB_DIR / "migrations").glob("*.sql")):
            await conn.execute(f.read_text(encoding="utf-8"))
    finally:
        await conn.close()
