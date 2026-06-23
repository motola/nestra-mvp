"""Shared FastAPI dependencies for the v1 API."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from db import AsyncSessionLocal, get_session
from identity.security import decode_access_token
from shared.tenant import set_org_context

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_org_scoped_session(
    authorization: Annotated[str | None, Header()] = None,
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a session with the org context set from the bearer token, when present.

    Authenticated requests are scoped to their organisation (RLS enforced for
    non-BYPASSRLS roles). Unauthenticated requests (e.g. demo mode) get no
    context set, so a BYPASSRLS connection still sees all rows.
    """
    async with AsyncSessionLocal() as session:
        if authorization and authorization.lower().startswith("bearer "):
            payload = decode_access_token(authorization.split(" ", 1)[1])
            if payload and payload.get("org"):
                await set_org_context(session, payload["org"])
        yield session


OrgScopedSessionDep = Annotated[AsyncSession, Depends(get_org_scoped_session)]
