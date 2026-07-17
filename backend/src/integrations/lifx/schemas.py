"""LIFX request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LifxDeviceIn(BaseModel):
    """Add LIFX device request."""

    lifx_id: str
    name: str
    device_type: str
    property_id: UUID


class LifxDeviceOut(BaseModel):
    """LIFX device response."""

    id: UUID
    property_id: UUID
    lifx_id: str
    name: str
    device_type: str
    online: bool
    raw_state: dict
    last_sync: datetime
    created_at: datetime
