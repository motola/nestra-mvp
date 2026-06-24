"""Bluetooth API request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BluetoothDeviceIn(BaseModel):
    """Input: pair a Bluetooth device."""

    mac_address: str = Field(..., description="Device MAC address (AA:BB:CC:DD:EE:FF)")
    name: str = Field(..., description="Device friendly name")
    property_id: UUID
    device_type: str = Field(default="unknown", description="Device type (light, sensor, etc.)")
    rssi: int = Field(default=-100, description="Signal strength in dBm")
    battery_level: int | None = Field(default=None, description="Battery level 0-100")


class BluetoothDeviceOut(BaseModel):
    """Output: Bluetooth device."""

    id: UUID
    property_id: UUID
    mac_address: str
    name: str
    device_type: str
    rssi: int
    battery_level: int | None
    is_paired: bool
    last_sync: datetime
    created_at: datetime


class BluetoothPairResponse(BaseModel):
    """Response: device paired successfully."""

    device_id: UUID
    status: str = "paired"
    message: str = "Device paired successfully"


class BluetoothUnpairResponse(BaseModel):
    """Response: device unpaired successfully."""

    status: str = "unpaired"
    message: str = "Device unpaired successfully"
