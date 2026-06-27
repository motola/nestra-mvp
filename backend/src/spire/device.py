"""SPIRE — the unified device resource model.

Smart Property Interoperability REsources. A vendor-agnostic device, structured
the way FHIR structures a resource: a logical identity, business identifiers, a
lifecycle status, typed content, and references to where it lives. Fields are
grouped by **owner**, so the structure documents the merge rules the repository
applies on every sync:

    identity     : assigned once, never changes
    status       : lifecycle, system/operator managed
    vendor       : overwritten on every sync (the vendor owns these values)
    naming       : user-owned, preserved across syncs (never clobbered)
    placement    : user-owned (the operator assigns the device to a property/room)
    connectivity : overwritten on every sync (live reachability)
    traits       : derived from the vendor's declared capabilities
    state        : overwritten on every sync (current values)
    meta         : system-managed provenance and timestamps

Every vendor normaliser must produce a SpireDevice.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from spire.traits import Trait

# Fixed namespace so a device's logical id is deterministic from its business
# identifier — the same physical device gets the same id on every sync.
_SPIRE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "spire:device")


class DeviceStatus(StrEnum):
    """Lifecycle of a device on the platform (mirrors FHIR's Device.status)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


class DeviceCategory(StrEnum):
    """Coarse kind, for grouping and iconography (mirrors FHIR's Device.type)."""

    LIGHT = "light"
    PLUG = "plug"
    SENSOR = "sensor"
    LOCK = "lock"
    THERMOSTAT = "thermostat"
    OTHER = "other"


class SpireIdentifier(BaseModel):
    """A business identifier from a source system (mirrors FHIR's Identifier)."""

    system: str  # the vendor namespace, e.g. "govee"
    value: str  # the vendor's stable id within that system, e.g. "AA::H6159"


class DeviceIdentity(BaseModel):
    """Identity — assigned once and never overwritten on sync.

    The logical ``id`` is derived deterministically from the business identifier,
    so resolving the same device twice always yields the same id.
    """

    identifier: SpireIdentifier
    id: str = ""

    @model_validator(mode="after")
    def _derive_id(self) -> DeviceIdentity:
        if not self.id:
            key = f"{self.identifier.system}:{self.identifier.value}"
            self.id = str(uuid.uuid5(_SPIRE_NAMESPACE, key))
        return self


class VendorRef(BaseModel):
    """Vendor-owned values — overwritten on every sync."""

    vendor: str  # dispatch key, e.g. "govee"
    vendor_name: str | None = None  # the vendor's own product name, informational
    model_number: str | None = None
    serial_number: str | None = None


class DeviceNaming(BaseModel):
    """User-owned — preserved across syncs, never clobbered by a vendor refresh."""

    display_name: str | None = None


class DevicePlacement(BaseModel):
    """Where the device lives and who owns it — operator-assigned (FHIR owner/location)."""

    organization_id: str | None = None
    property_id: str | None = None
    room_id: str | None = None


class Connectivity(BaseModel):
    """Live reachability — overwritten on every sync."""

    online: bool = False
    ip_address: str | None = None
    mac: str | None = None
    signal_strength: int | None = None  # RSSI in dBm, when the vendor reports it
    last_seen: datetime | None = None


class AuditMeta(BaseModel):
    """System-managed provenance and timestamps (mirrors FHIR's meta)."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_synced_at: datetime | None = None
    source: str | None = None  # the integration that produced this resource
    version_id: int = 1  # bumped by the repository on each update


class SpireDevice(BaseModel):
    """The unified SPIRE device resource."""

    resource_type: Literal["Device"] = "Device"
    identity: DeviceIdentity
    status: DeviceStatus = DeviceStatus.ACTIVE
    category: DeviceCategory = DeviceCategory.OTHER
    vendor: VendorRef
    naming: DeviceNaming = Field(default_factory=DeviceNaming)
    placement: DevicePlacement = Field(default_factory=DevicePlacement)
    connectivity: Connectivity = Field(default_factory=Connectivity)
    traits: list[Trait] = Field(default_factory=list)
    supported_commands: list[str] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
    meta: AuditMeta = Field(default_factory=AuditMeta)

    @property
    def label(self) -> str:
        """The name to show a user: their own name first, then the vendor's, then a fallback."""
        return (
            self.naming.display_name
            or self.vendor.vendor_name
            or f"Device {self.identity.identifier.value}"
        )

    @property
    def online(self) -> bool:
        """Convenience accessor — live reachability lives under connectivity."""
        return self.connectivity.online

    def supports(self, trait: Trait) -> bool:
        """Whether this device exposes a given trait."""
        return trait in self.traits

    @property
    def controllable(self) -> bool:
        """True if the device exposes any actuator trait (not a pure sensor)."""
        return any(trait in _ACTUATOR_TRAITS for trait in self.traits)

    def to_api(self) -> dict[str, Any]:
        """Flatten to the wire shape the current frontend consumes.

        The internal model is rich and grouped; the API contract stays flat so
        the read path and frontend are untouched while we migrate onto SPIRE.
        """
        state = self.state
        return {
            "id": self.identity.id,
            "vendor_id": self.identity.identifier.value,
            "vendor": self.vendor.vendor,
            "name": self.label,
            "type": self.category.value,
            "online": self.connectivity.online,
            "controllable": self.controllable,
            "state": state,
            "power_draw": state.get("power"),
            "temperature": state.get("temperature"),
            "humidity": state.get("humidity"),
            "leak_detected": state.get("leak_detected"),
            "property_id": self.placement.property_id,
            "room_id": self.placement.room_id,
            "last_seen": self.meta.last_synced_at or self.meta.updated_at,
            "supported_commands": self.supported_commands,
            "traits": [trait.value for trait in self.traits],
        }


_ACTUATOR_TRAITS = frozenset(
    {Trait.ON_OFF, Trait.DIMMABLE, Trait.COLOR, Trait.COLOR_TEMP, Trait.LOCKABLE}
)
