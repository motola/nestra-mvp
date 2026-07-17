"""Shelly local-network adapter."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

from property.domain import Device

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
        """Fetch Shelly devices. Note: Shelly requires device registry/config."""
        return []

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
