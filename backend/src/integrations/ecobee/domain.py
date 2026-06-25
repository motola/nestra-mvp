"""Ecobee Thermostat domain model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EcobeeDevice(BaseModel):
    """An Ecobee Thermostat installed on a property."""

    id: UUID
    property_id: UUID
    integration_id: UUID
    device_id: str  # Ecobee device ID
    name: str  # e.g., "Main Floor", "Upstairs"
    current_temperature: float  # in Celsius or Fahrenheit
    target_temperature: float
    mode: str  # "heat", "cool", "auto", "off"
    humidity: int  # 0-100 percentage
    is_online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
