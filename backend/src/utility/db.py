from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import get_settings


def _make_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=settings.debug)


# Module-level singletons — created once on first import.
engine: AsyncEngine = _make_engine()
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


@asynccontextmanager
async def org_scope(
    session: AsyncSession,
    organization_id: UUID,
    user_id: UUID | None = None,
) -> AsyncIterator[None]:
    """Set Postgres session variables required by RLS policies.

    Must wrap every query on tenant-scoped tables. Uses SET LOCAL so the
    variables are automatically cleared at the end of the transaction.
    """
    await session.execute(
        text("SET LOCAL app.current_organization_id = :org_id"),
        {"org_id": str(organization_id)},
    )
    if user_id is not None:
        await session.execute(
            text("SET LOCAL app.current_user_id = :user_id"),
            {"user_id": str(user_id)},
        )
    yield
