"""TP-Link Smart Plug domain model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TPlinkPlug(BaseModel):
    """A TP-Link Smart Plug installed on a property."""

    id: UUID
    property_id: UUID
    integration_id: UUID
    device_id: str
    name: str
    power_state: bool
    power_usage_w: float  # Current power consumption
    is_online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
