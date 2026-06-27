"""
SpireDevice — the single, vendor-agnostic device model used everywhere
in the platform. Every vendor normaliser must produce this model as output.
Nothing in services/, api/, or frontend should ever reference a vendor-specific
field name. This is the single most important architectural rule in the codebase.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from spire.traits import Trait, derive_traits

DeviceType = Literal["plug", "light", "sensor", "lock", "thermostat"]

# Fixed namespace so a device's id is deterministic from its vendor identity —
# the same physical device gets the same id on every poll, across runs/machines.
_DEVICE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "spire:device")


class SpireDevice(BaseModel):
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

    # Capabilities. Each normaliser sets these from the vendor's declared
    # capabilities; the validator below is only a fallback for producers that
    # don't (e.g. the state-only poll path and seed data).
    traits: list[Trait] = Field(default_factory=list)

    @model_validator(mode="after")
    def _ensure_stable_id(self) -> SpireDevice:
        """Derive a deterministic id from the vendor identity when one isn't given,
        so the same physical device keeps the same id across every poll/sync."""
        if not self.id:
            self.id = str(uuid.uuid5(_DEVICE_NAMESPACE, f"{self.vendor}:{self.vendor_id}"))
        return self

    @model_validator(mode="after")
    def _ensure_traits(self) -> SpireDevice:
        """Fallback: derive capabilities from the canonical fields if a producer didn't
        set them, so no device is ever left without a capability set."""
        if not self.traits:
            self.traits = derive_traits(
                self.supported_commands,
                reports_power=self.power_draw is not None,
                reports_temperature=self.temperature is not None,
                reports_humidity=self.humidity is not None,
                reports_leak=self.leak_detected is not None,
            )
        return self
