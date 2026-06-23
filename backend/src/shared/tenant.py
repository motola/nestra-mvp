"""Tenant scoping — sets the Postgres setting that Row-Level Security reads.

RLS policies on tenant-scoped tables compare ``organisation_id`` against
``current_setting('app.current_organization_id')``. Setting it with
``is_local = true`` scopes it to the current transaction, so it cannot leak
between pooled requests. This only *enforces* isolation for roles that do not
have ``BYPASSRLS`` — see ``docs/class_diagrams.md`` (RLS Implications).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_SET_ORG_CONTEXT = text("SELECT set_config('app.current_organization_id', :org_id, true)")


async def set_org_context(session: AsyncSession, organization_id: UUID | str) -> None:
    """Bind the active organisation for the current transaction (RLS reads this)."""
    await session.execute(_SET_ORG_CONTEXT, {"org_id": str(organization_id)})


@asynccontextmanager
async def org_scope(
    session: AsyncSession, organization_id: UUID | str
) -> AsyncGenerator[AsyncSession, None]:
    """Scope queries on ``session`` to one organisation for the current transaction."""
    await set_org_context(session, organization_id)
    yield session
