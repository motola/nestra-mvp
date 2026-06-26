"""August Smart Lock domain model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AugustLock(BaseModel):
    """An August Smart Lock installed on a property."""

    id: UUID
    property_id: UUID
    integration_id: UUID
    lock_id: str  # August device ID (unique per organization)
    name: str  # e.g., "Front Door", "Unit 101"
    location: str  # Building, unit, or descriptive location
    battery_level: int  # 0-100 percentage
    is_locked: bool  # Current lock state
    is_online: bool  # Device connectivity
    model: str  # August device model
    last_sync: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
