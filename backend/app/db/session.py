from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from ..core.config import settings


# 호스팅 서비스가 주는 postgres://…?sslmode=require 형식을 asyncpg용 URL + ssl 여부로
def split_dsn(url: str) -> tuple[str, bool]:
    p = urlsplit(url)
    q = dict(parse_qsl(p.query))
    ssl = q.pop("sslmode", "") in ("require", "verify-ca", "verify-full")
    return urlunsplit(("postgresql+asyncpg", p.netloc, p.path, urlencode(q), "")), ssl


_url, _ssl = split_dsn(settings.database_url)
engine = create_async_engine(_url, pool_pre_ping=True, connect_args={"ssl": True} if _ssl else {})
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# 요청 단위 DB 세션 의존성
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
