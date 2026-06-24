"""Hikvision Camera API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HikvisionCameraIn(BaseModel):
    """Input: add a Hikvision Camera."""

    camera_id: str = Field(..., description="Hikvision camera ID")
    name: str = Field(..., description="Camera name")
    property_id: UUID
    location: str = Field(default="Unknown", description="Location in property")
    is_online: bool = Field(default=True)
    stream_url: str = Field(default="", description="RTSP stream URL")


class HikvisionCameraOut(BaseModel):
    """Output: Hikvision Camera."""

    id: UUID
    property_id: UUID
    camera_id: str
    name: str
    location: str
    is_online: bool
    stream_url: str
    last_sync: datetime
    created_at: datetime


class HikvisionStatusResponse(BaseModel):
    """Response: camera action successful."""

    status: str = "success"
    message: str = "Camera updated"
