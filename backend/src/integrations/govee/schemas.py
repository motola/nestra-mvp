"""Govee request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GoveeDeviceIn(BaseModel):
    """Add Govee device request."""

    govee_id: str
    name: str
    device_type: str
    property_id: UUID


class GoveeDeviceOut(BaseModel):
    """Govee device response."""

    id: UUID
    property_id: UUID
    govee_id: str
    name: str
    device_type: str
    online: bool
    raw_state: dict
    last_sync: datetime
    created_at: datetime
