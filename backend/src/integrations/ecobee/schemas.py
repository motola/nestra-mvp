"""Ecobee Thermostat API request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EcobeeDeviceIn(BaseModel):
    """Input: add an Ecobee Thermostat to a property."""

    device_id: str = Field(..., description="Ecobee device ID")
    name: str = Field(..., description="Thermostat name (e.g., 'Main Floor')")
    property_id: UUID
    current_temperature: float = Field(..., description="Current temperature")
    target_temperature: float = Field(..., description="Target temperature")
    mode: str = Field(default="auto", description="Mode: heat, cool, auto, off")
    humidity: int = Field(default=50, ge=0, le=100, description="Humidity 0-100")


class EcobeeDeviceOut(BaseModel):
    """Output: Ecobee Thermostat."""

    id: UUID
    property_id: UUID
    device_id: str
    name: str
    current_temperature: float
    target_temperature: float
    mode: str
    humidity: int
    is_online: bool
    last_sync: datetime
    created_at: datetime


class EcobeeTemperatureUpdate(BaseModel):
    """Input: update thermostat temperature."""

    device_id: UUID
    target_temperature: float = Field(..., description="New target temperature")


class EcobeeStatusResponse(BaseModel):
    """Response: thermostat action successful."""

    status: str = "success"
    message: str = "Thermostat updated"
