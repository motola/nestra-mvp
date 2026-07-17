"""Matter request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class MatterDeviceIn(BaseModel):
    """Add Matter device request."""

    matter_id: str
    name: str
    device_type: str
    property_id: UUID


class MatterDeviceOut(BaseModel):
    """Matter device response."""

    id: UUID
    property_id: UUID
    matter_id: str
    name: str
    device_type: str
    online: bool
    raw_state: dict[str, Any]
    last_sync: datetime
    created_at: datetime
