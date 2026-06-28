"""Shared FastAPI dependencies for the v1 API."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from common.tenant import set_org_context
from config import Settings, get_settings
from db import AsyncSessionLocal, get_session
from identity.security import decode_access_token


def get_effective_settings(
    x_show_demo: Annotated[str | None, Header()] = None,
) -> Settings:
    """Settings for the request, with demo data hidden unless explicitly asked for.

    Demo seeding only appears when the deployment enables it (``DEMO_MODE``) AND
    the request opts in with ``X-Show-Demo: 1``. So by default — and for any
    client that doesn't send the header (i.e. anyone a customer would see) — no
    demo data is served anywhere. The toggle is a deliberate, hidden opt-in.
    """
    settings = get_settings()
    if settings.demo_mode and x_show_demo != "1":
        return settings.model_copy(update={"demo_mode": False})
    return settings


SettingsDep = Annotated[Settings, Depends(get_effective_settings)]
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
