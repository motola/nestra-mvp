"""Property domain models — portfolios, properties, devices, and integrations."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceType(StrEnum):
    """Types of smart home devices."""

    LOCK = "lock"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    PLUG = "plug"
    SENSOR = "sensor"
    SPEAKER = "speaker"
    LIGHT = "light"


class Integration(BaseModel):
    """Integration connection to a vendor (Bluetooth, WiFi, etc)."""

    id: UUID | None = None
    organization_id: UUID
    vendor: str
    account_identifier: str = ""
    enabled: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class Property(BaseModel):
    """A property (building/asset) within a portfolio."""

    id: UUID | None = None
    portfolio_id: UUID
    organization_id: UUID
    name: str
    address: str
    description: str | None = None
    timezone: str = "UTC"
    property_type: str
    units: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class Device(BaseModel):
    """Unified smart home device across all integrations."""

    id: UUID | None = None
    organization_id: UUID
    portfolio_id: UUID
    property_id: UUID
    integration_id: UUID
    device_type: DeviceType
    vendor: str
    vendor_specific_id: str
    vendor_name: str | None = None
    online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
    raw_state: dict[str, object] = Field(default_factory=dict)

    model_config = {"frozen": False}
