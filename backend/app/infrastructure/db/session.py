from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()

_engine_kwargs: dict = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}

_url = settings.resolved_database_url
if settings.is_postgres:
    if settings.supabase_use_pooler:
        # Pooler Supabase (porta 6543) — melhor para muitas conexões curtas
        _engine_kwargs["poolclass"] = NullPool
    else:
        _engine_kwargs["pool_size"] = settings.db_pool_size
        _engine_kwargs["max_overflow"] = settings.db_max_overflow
        _engine_kwargs["pool_recycle"] = settings.db_pool_recycle

engine = create_async_engine(_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    await engine.dispose()
