"""Integration adapter protocol — per-vendor contract for device sync."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from property.domain import Device


class IntegrationAdapter(Protocol):
    """Protocol: vendor-specific device adapter.

    Adapters interpret vendor payloads, build canonical devices via
    create_device_data(), and perform vendor-specific control. They
    never import or call the repository.
    """

    vendor: str

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Fetch devices from vendor, interpret payloads, return canonical devices.

        No persistence — returns only in-memory Device objects with id=None.
        """
        ...

    async def fetch_state(self, device: Device) -> Device:
        """Refresh a device's current state from vendor.

        Returns the same device with updated online/raw_state/last_sync.
        Preserves id, display_name, created_at, organization_id.
        """
        ...

    async def execute(self, device: Device, command: str, params: dict[str, object]) -> bool:
        """Execute a control command on the device.

        command: string like "turn_on", "set_brightness", etc.
        params: dict of command-specific parameters.
        Returns True iff the command succeeded.
        """
        ...
