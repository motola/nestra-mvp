"""August Smart Lock API request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AugustLockIn(BaseModel):
    """Input: add an August Smart Lock to a property."""

    lock_id: str = Field(..., description="August device ID")
    name: str = Field(..., description="Lock name (e.g., 'Front Door')")
    location: str = Field(..., description="Location description")
    property_id: UUID
    battery_level: int = Field(default=100, ge=0, le=100, description="Battery level 0-100")
    is_locked: bool = Field(default=True, description="Current lock state")
    model: str = Field(default="August Pro", description="Device model")


class AugustLockOut(BaseModel):
    """Output: August Smart Lock."""

    id: UUID
    property_id: UUID
    lock_id: str
    name: str
    location: str
    battery_level: int
    is_locked: bool
    is_online: bool
    model: str
    last_sync: datetime
    created_at: datetime


class AugustLockStatusUpdate(BaseModel):
    """Input: update lock status (lock/unlock)."""

    lock_id: UUID
    is_locked: bool = Field(..., description="Lock state: true=locked, false=unlocked")


class AugustStatusResponse(BaseModel):
    """Response: lock action successful."""

    status: str = "success"
    message: str = "Lock action completed"


class AugustLockListResponse(BaseModel):
    """Response: list of locks."""

    locks: list[AugustLockOut]
    total: int
