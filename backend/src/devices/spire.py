"""SPIRE — the unified device resource model.

Smart Property Interoperability REsources. A vendor-agnostic device, structured
the way FHIR structures a resource: a logical identity, business identifiers, and
typed content. Fields are grouped by **owner**, so the structure itself documents
the merge rules the repository applies on every sync:

    identity : assigned once, never changes
    vendor   : overwritten on every sync (the vendor owns these values)
    naming   : user-owned, preserved across syncs (never clobbered)
    meta     : system-managed timestamps

Every vendor normaliser must produce a SpireDevice. Nothing downstream should
reference a vendor-specific field name.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from devices.capabilities import Capability

# Fixed namespace so a device's logical id is deterministic from its business
# identifier — the same physical device gets the same id on every sync.
_SPIRE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "spire:device")


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
    serial_number: str | None = None


class DeviceNaming(BaseModel):
    """User-owned — preserved across syncs, never clobbered by a vendor refresh."""

    display_name: str | None = None


class AuditMeta(BaseModel):
    """System-managed timestamps (mirrors FHIR's meta)."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_synced_at: datetime | None = None


class SpireDevice(BaseModel):
    """The unified SPIRE device resource."""

    resource_type: Literal["Device"] = "Device"
    identity: DeviceIdentity
    vendor: VendorRef
    naming: DeviceNaming = Field(default_factory=DeviceNaming)
    capabilities: list[Capability] = Field(default_factory=list)
    online: bool = False
    raw_state: dict[str, Any] = Field(default_factory=dict)
    meta: AuditMeta = Field(default_factory=AuditMeta)

    @property
    def label(self) -> str:
        """The name to show a user: their own name first, then the vendor's, then a fallback."""
        return (
            self.naming.display_name
            or self.vendor.vendor_name
            or f"Device {self.identity.identifier.value}"
        )

    def supports(self, capability: Capability) -> bool:
        """Whether this device exposes a given capability."""
        return capability in self.capabilities
