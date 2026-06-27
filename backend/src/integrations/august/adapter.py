"""August Smart Locks adapter — normalizes August locks to AlphaconDevice."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from integrations.adapter import IntegrationAdapter
from property.domain import Device, DeviceType


class AugustAdapter(IntegrationAdapter):
    """Adapter for August Smart Lock devices."""

    @property
    def device_type(self) -> DeviceType:
        return DeviceType.LOCK

    @property
    def vendor_name(self) -> str:
        return "August"

    async def to_device(
        self,
        vendor_device: object,
        property_id: UUID,
        integration_id: UUID,
    ) -> Device:
        """Convert August lock to AlphaconDevice."""
        if not isinstance(vendor_device, dict):
            raise ValueError("Invalid August device")

        lock: dict[str, Any] = vendor_device
        return self._build_device(
            device_id=lock["id"],
            property_id=property_id,
            integration_id=integration_id,
            name=lock["name"],
            vendor_specific_id=lock["lock_id"],
            online=lock["is_online"],
            raw_state={
                "is_locked": lock["is_locked"],
                "battery_level": lock["battery_level"],
                "model": lock["model"],
            },
        )

    async def execute_command(
        self, device: Device, command: str, params: dict[str, object]
    ) -> bool:
        """Execute lock/unlock command."""
        return command in ("lock", "unlock")
