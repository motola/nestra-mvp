from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

from config import Settings, get_settings


class Organization(BaseModel):
    """Organization context."""

    id: UUID


# Type alias used on every endpoint that needs access to app settings.
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_organization() -> Organization:
    """Get current organization context.

    TODO: Implement proper authentication and organization context.
    For now, this is a placeholder that will be implemented once identity
    service is fully integrated.
    """
    # This will be replaced with actual authentication logic
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Organization context not yet implemented",
    )


OrganizationDep = Annotated[Organization, Depends(get_organization)]

# CurrentUser and TenantScope dependencies are added in Batch 5 once the
# identity context exists.
