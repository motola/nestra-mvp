"""Async database engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_settings

_settings = get_settings()

# Normalise postgresql:// → postgresql+asyncpg:// if needed
_url = _settings.database_url
if _url.startswith("postgresql://") and "+asyncpg" not in _url:
    _url = "postgresql+asyncpg://" + _url[len("postgresql://") :]

engine = create_async_engine(_url, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
