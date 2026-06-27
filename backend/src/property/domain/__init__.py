"""Property domain models — properties and devices."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Types of smart home devices."""

    LOCK = "lock"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    PLUG = "plug"
    SENSOR = "sensor"
    SPEAKER = "speaker"


class Device(BaseModel):
    """Unified smart home device across all integrations."""

    id: UUID | None
    organization_id: UUID
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
