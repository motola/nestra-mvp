"""Shelly request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ShellyDeviceIn(BaseModel):
    """Add Shelly device request."""

    shelly_id: str
    name: str
    ip_address: str
    property_id: UUID


class ShellyDeviceOut(BaseModel):
    """Shelly device response."""

    id: UUID
    property_id: UUID
    shelly_id: str
    name: str
    ip_address: str
    online: bool
    raw_state: dict[str, Any]
    last_sync: datetime
    created_at: datetime
