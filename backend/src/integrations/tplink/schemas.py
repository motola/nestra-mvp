"""TP-Link Smart Plug API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TPlinkPlugIn(BaseModel):
    """Input: add a TP-Link Smart Plug."""

    device_id: str = Field(..., description="TP-Link device ID")
    name: str = Field(..., description="Plug name")
    property_id: UUID
    power_state: bool = Field(default=False, description="Current power state")
    power_usage_w: float = Field(default=0.0, description="Power usage in watts")


class TPlinkPlugOut(BaseModel):
    """Output: TP-Link Smart Plug."""

    id: UUID
    property_id: UUID
    device_id: str
    name: str
    power_state: bool
    power_usage_w: float
    is_online: bool
    last_sync: datetime
    created_at: datetime


class TPlinkPowerStateUpdate(BaseModel):
    """Input: update power state."""

    device_id: UUID
    power_state: bool


class TPlinkStatusResponse(BaseModel):
    """Response: plug action successful."""

    status: str = "success"
    message: str = "Plug updated"
