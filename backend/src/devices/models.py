"""
AlphaconDevice — the single, vendor-agnostic device model used everywhere
in the platform. Every vendor normaliser must produce this model as output.
Nothing in services/, api/, or frontend should ever reference a vendor-specific
field name. This is the single most important architectural rule in the codebase.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DeviceType = Literal["plug", "light", "sensor", "lock", "thermostat"]
VendorName = Literal["govee", "shelly", "lifx"]


class AlphaconDevice(BaseModel):
    """Vendor-agnostic device representation. Output type for all normalisers."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vendor_id: str
    vendor: str
    name: str
    type: str
    online: bool
    controllable: bool
    state: dict[str, Any] = Field(default_factory=dict)

    # Plug-specific
    power_draw: float | None = None

    # Sensor-specific
    temperature: float | None = None
    humidity: float | None = None
    leak_detected: bool | None = None

    property_id: str | None = None
    room_id: str | None = None
    last_seen: datetime = Field(default_factory=lambda: datetime.now(UTC))
    supported_commands: list[str] = Field(default_factory=list)
