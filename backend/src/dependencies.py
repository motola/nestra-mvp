from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import Settings, get_settings

__all__ = ["SettingsDep", "UserDep", "security", "get_current_user"]

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


UserDep = Annotated[UUID, Depends(get_current_user)]

# CurrentUser and TenantScope dependencies are added in Batch 5 once the
# identity context exists.
