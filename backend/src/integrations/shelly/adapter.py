"""Shelly local-network adapter."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

from property.domain import Device, DeviceType

logger = logging.getLogger(__name__)

_TIMEOUT = 5.0


class ShellyLocalController:
    """Direct local-network controller for Shelly devices."""

    def __init__(self, ip: str) -> None:
        self.ip = ip

    async def get_state(self) -> dict[str, Any]:
        """Get device state via RPC."""
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"http://{self.ip}/rpc/Switch.GetStatus",
                json={"id": 0},
            )
            r.raise_for_status()
            data = r.json()
            aenergy = data.get("aenergy") or {}
            return {
                "on": data.get("output", False),
                "power": float(data.get("apower", 0.0)),
                "voltage": float(data.get("voltage", 0.0)),
                "current": float(data.get("current", 0.0)),
                "energy": float(aenergy.get("total", 0.0)),
            }

    async def turn_on(self) -> bool:
        """Turn on the relay."""
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.post(
                    f"http://{self.ip}/rpc/Switch.Set",
                    json={"id": 0, "on": True},
                )
                r.raise_for_status()
                return True
        except Exception as exc:
            logger.warning("Shelly turn_on failed for %s: %s", self.ip, exc)
            return False

    async def turn_off(self) -> bool:
        """Turn off the relay."""
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.post(
                    f"http://{self.ip}/rpc/Switch.Set",
                    json={"id": 0, "on": False},
                )
                r.raise_for_status()
                return True
        except Exception as exc:
            logger.warning("Shelly turn_off failed for %s: %s", self.ip, exc)
            return False


class ShellyAdapter:
    """Adapter for local Shelly devices."""

    vendor = "shelly"

    def __init__(self) -> None:
        self._controllers: dict[str, ShellyLocalController] = {}

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Fetch Shelly devices. Returns mock devices for testing."""
        from datetime import UTC, datetime

        return [
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="shelly",
                vendor_specific_id="shelly_plug_s_1",
                vendor_name="Shelly Plug S",
                device_type=DeviceType.PLUG,
                online=True,
                raw_state={"on": True, "power": 45.2, "ip": "192.168.1.100"},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="shelly",
                vendor_specific_id="shelly_1pm_2",
                vendor_name="Shelly 1PM",
                device_type=DeviceType.PLUG,
                online=True,
                raw_state={"on": False, "power": 0.0, "ip": "192.168.1.101"},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

    async def fetch_state(self, device: Device) -> Device:
        """Refresh device state from Shelly."""
        if device.vendor_specific_id not in self._controllers:
            ip = device.raw_state.get("ip")
            if not ip:
                device.online = False
                return device
            self._controllers[device.vendor_specific_id] = ShellyLocalController(str(ip))

        try:
            controller = self._controllers[device.vendor_specific_id]
            state = await controller.get_state()
            device.online = True
            device.raw_state = state
        except Exception as exc:
            logger.warning("Failed to fetch Shelly state: %s", exc)
            device.online = False

        return device

    async def execute(self, device: Device, command: str, params: dict[str, Any]) -> bool:
        """Execute command on Shelly device."""
        ip = device.raw_state.get("ip")
        if not ip:
            return False

        controller = ShellyLocalController(str(ip))

        if command == "turn_on":
            return await controller.turn_on()
        elif command == "turn_off":
            return await controller.turn_off()
        else:
            logger.warning("Unknown Shelly command: %s", command)
            return False
