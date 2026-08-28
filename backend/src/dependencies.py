from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import Settings, get_settings

__all__ = ["SettingsDep", "UserDep", "security", "get_current_user", "get_current_organization"]

# Type alias used on every endpoint that needs access to app settings.
SettingsDep = Annotated[Settings, Depends(get_settings)]

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials,
    settings: SettingsDep,
) -> UUID:
    """Extract and verify JWT token, return user ID."""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return UUID(user_id)
    except (jwt.InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_organization(
    credentials: HTTPAuthorizationCredentials,
    settings: SettingsDep,
) -> UUID:
    """Extract organization ID from JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        org_id = payload.get("org")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return UUID(org_id)
    except (jwt.InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


UserDep = Annotated[UUID, Depends(get_current_user)]
OrgDep = Annotated[UUID, Depends(get_current_organization)]

# CurrentUser and TenantScope dependencies are added in Batch 5 once the
# identity context exists.
