from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class Room(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_id: str
    name: str
    floor: int | None = None
    device_count: int = 0
    alert_count: int = 0


class RoomCreate(BaseModel):
    name: str
    floor: int | None = None
