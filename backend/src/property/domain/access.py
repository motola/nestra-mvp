"""Device access grant domain models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class AccessType(StrEnum):
    """Access grant types."""

    READ = "read"
    CONTROL = "control"
    MANAGE = "manage"


class DeviceAccessGrant(BaseModel):
    """Grant of access to a device for a specific user."""

    id: UUID | None = None
    organization_id: UUID
    device_id: UUID
    grantee_user_id: UUID | None = None
    grantee_email: str | None = None
    granted_by_user_id: UUID
    access_type: str  # "read", "control", "manage"
    capabilities: list[str] = []
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None = None

    model_config = {"frozen": False}
