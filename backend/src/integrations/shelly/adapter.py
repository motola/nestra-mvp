"""Shelly local-network and cloud adapter."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from property.domain import Device

logger = logging.getLogger(__name__)

_TIMEOUT = 5.0
SHELLY_CLOUD_URL = "https://shelly-api.shelly.cloud/info"


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
    """Adapter for Shelly devices (cloud and local)."""

    vendor = "shelly"

    def __init__(self) -> None:
        self._controllers: dict[str, ShellyLocalController] = {}

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        auth_token: str | None = None,
    ) -> list[Device]:
        """Fetch Shelly devices from cloud API.

        Requires Shelly auth token.
        Falls back to mock data if no token provided.
        """
        if not auth_token:
            logger.warning("No Shelly auth token provided, returning mock devices")
            return self._get_mock_devices(organization_id, property_id, integration_id)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{SHELLY_CLOUD_URL}",
                    headers={"Authorization": f"Bearer {auth_token}"},
                )
                response.raise_for_status()
                data = response.json()

                devices = []
                for device_data in data.get("devices", []):
                    device = Device(
                        id=None,
                        organization_id=organization_id,
                        property_id=property_id,
                        integration_id=integration_id,
                        vendor="shelly",
                        vendor_specific_id=device_data.get("id", ""),
                        vendor_name=device_data.get("name", "Shelly Device"),
                        device_type=self._get_device_type(device_data.get("model", "")),
                        online=device_data.get("online", False),
                        raw_state={
                            "on": device_data.get("status", {})
                            .get("switch:0", {})
                            .get("output", False),
                            "power": device_data.get("status", {})
                            .get("switch:0", {})
                            .get("apower", 0.0),
                            "ip": device_data.get("addr", ""),
                        },
                        last_sync=datetime.now(UTC),
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    devices.append(device)

                logger.info(f"Fetched {len(devices)} Shelly devices")
                return devices
        except Exception as e:
            logger.error(f"Failed to fetch Shelly devices: {e}")
            logger.info("Falling back to mock devices")
            return self._get_mock_devices(organization_id, property_id, integration_id)

    def _get_device_type(self, model: str) -> str:
        """Map Shelly model to device type."""
        if "plug" in model.lower() or "switch" in model.lower():
            return "PLUG"
        if "dimmer" in model.lower():
            return "LIGHT"
        if "door" in model.lower():
            return "SENSOR"
        return "PLUG"

    def _get_mock_devices(
        self,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Return mock Shelly devices for testing."""
        return [
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="shelly",
                vendor_specific_id="shelly_plug_s_1",
                vendor_name="Shelly Plug S",
                device_type="PLUG",
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
                device_type="PLUG",
                online=True,
                raw_state={"on": False, "power": 0.0, "ip": "192.168.1.101"},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

    async def fetch_state(self, device: Device, auth_token: str | None = None) -> Device:
        """Refresh device state from Shelly (cloud or local)."""
        if auth_token:
            return await self._fetch_state_cloud(device, auth_token)
        else:
            return await self._fetch_state_local(device)

    async def _fetch_state_cloud(self, device: Device, auth_token: str) -> Device:
        """Refresh device state via Shelly cloud API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{SHELLY_CLOUD_URL}",
                    headers={"Authorization": f"Bearer {auth_token}"},
                )
                response.raise_for_status()
                data = response.json()

                for dev in data.get("devices", []):
                    if dev.get("id") == device.vendor_specific_id:
                        device.online = dev.get("online", False)
                        device.raw_state = {
                            "on": dev.get("status", {}).get("switch:0", {}).get("output", False),
                            "power": dev.get("status", {}).get("switch:0", {}).get("apower", 0.0),
                            "ip": dev.get("addr", ""),
                        }
                        device.updated_at = datetime.now(UTC)
                        return device
        except Exception as e:
            logger.warning(f"Failed to fetch Shelly cloud state: {e}")

        return device

    async def _fetch_state_local(self, device: Device) -> Device:
        """Refresh device state via local network."""
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
            device.updated_at = datetime.now(UTC)
        except Exception as exc:
            logger.warning("Failed to fetch Shelly local state: %s", exc)
            device.online = False

        return device

    async def execute(
        self, device: Device, command: str, params: dict[str, Any], auth_token: str | None = None
    ) -> bool:
        """Execute command on Shelly device (cloud or local)."""
        if auth_token:
            return await self._execute_cloud(device, command, auth_token)
        else:
            return await self._execute_local(device, command)

    async def _execute_cloud(self, device: Device, command: str, auth_token: str) -> bool:
        """Execute command via cloud API."""
        try:
            action = "on" if command == "turn_on" else "off"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{SHELLY_CLOUD_URL}/switch/{device.vendor_specific_id}/{action}",
                    headers={"Authorization": f"Bearer {auth_token}"},
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to execute cloud command: {e}")
            return False

    async def _execute_local(self, device: Device, command: str) -> bool:
        """Execute command via local network."""
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
