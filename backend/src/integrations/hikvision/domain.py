"""Hikvision Camera domain model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HikvisionCamera(BaseModel):
    """A Hikvision Camera installed on a property."""

    id: UUID
    property_id: UUID
    integration_id: UUID
    camera_id: str
    name: str
    location: str
    is_online: bool
    stream_url: str
    last_sync: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
