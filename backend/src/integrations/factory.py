"""Device factory — builds canonical devices in memory (no persistence)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device, DeviceType


def create_device_data(
    *,
    organization_id: UUID,
    property_id: UUID,
    integration_id: UUID,
    vendor: str,
    vendor_specific_id: str,
    vendor_name: str | None,
    device_type: DeviceType,
    online: bool,
    raw_state: dict[str, object] | None = None,
) -> Device:
    """Build a CanonicalDevice in memory. id is left for repository to assign.

    Performs NO I/O, NO database access. Only constructs the object.
    Timestamps are tz-aware UTC, set once in this function.
    """
    now = datetime.now(UTC)
    return Device(
        id=None,  # repository assigns on insert
        organization_id=organization_id,
        property_id=property_id,
        integration_id=integration_id,
        vendor=vendor,
        vendor_specific_id=vendor_specific_id,
        vendor_name=vendor_name,
        device_type=device_type,
        online=online,
        raw_state=raw_state or {},
        last_sync=now,
        created_at=now,
        updated_at=now,
    )
