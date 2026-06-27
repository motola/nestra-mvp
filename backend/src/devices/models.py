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

from pydantic import BaseModel, Field, model_validator

DeviceType = Literal["plug", "light", "sensor", "lock", "thermostat"]

# Fixed namespace so a device's id is deterministic from its vendor identity —
# the same physical device gets the same id on every poll, across runs/machines.
_DEVICE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "alphacon:device")


class AlphaconDevice(BaseModel):
    """Vendor-agnostic device representation. Output type for all normalisers."""

    id: str = ""  # derived deterministically from vendor identity if not supplied
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

    @model_validator(mode="after")
    def _ensure_stable_id(self) -> AlphaconDevice:
        """Derive a deterministic id from the vendor identity when one isn't given,
        so the same physical device keeps the same id across every poll/sync."""
        if not self.id:
            self.id = str(uuid.uuid5(_DEVICE_NAMESPACE, f"{self.vendor}:{self.vendor_id}"))
        return self
