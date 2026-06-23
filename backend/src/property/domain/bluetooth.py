from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BluetoothDevice(BaseModel):
    """A Bluetooth device discovered and paired in a property."""

    id: UUID
    property_id: UUID
    integration_id: UUID
    mac_address: str  # unique per organization
    name: str  # friendly name from Web Bluetooth API
    device_type: str  # inferred from advertised services (e.g., "light", "sensor")
    rssi: int  # signal strength in dBm (-100 to -20 typical)
    battery_level: int | None = None  # 0-100, if available
    is_paired: bool = True
    last_sync: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
