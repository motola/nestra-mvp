"""Meross adapter — normalizes Meross devices to unified Device model."""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from property.domain import Device

logger = logging.getLogger(__name__)

MEROSS_API_URL = "https://iot.meross.com/v1"


class MerossAdapter:
    """Adapter for Meross devices."""

    vendor = "meross"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        access_token: str | None = None,
    ) -> list[Device]:
        """Fetch Meross devices from cloud API.

        Requires Meross access token.
        Falls back to mock data if no token provided.
        """
        if not access_token:
            logger.warning("No Meross access token provided, returning mock devices")
            return self._get_mock_devices(organization_id, property_id, integration_id)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(
                    f"{MEROSS_API_URL}/homekit/devices",
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                devices = []
                for device_data in data.get("data", []):
                    device = Device(
                        id=None,
                        organization_id=organization_id,
                        property_id=property_id,
                        integration_id=integration_id,
                        vendor="meross",
                        vendor_specific_id=device_data.get("deviceId", ""),
                        vendor_name=device_data.get("deviceName", "Meross Device"),
                        device_type=self._get_device_type(device_data.get("deviceType", "")),
                        online=device_data.get("status") == "online",
                        raw_state=device_data.get("lastStatus", {}),
                        last_sync=datetime.now(UTC),
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    devices.append(device)

                logger.info(f"Fetched {len(devices)} Meross devices")
                return devices
        except Exception as e:
            logger.error(f"Failed to fetch Meross devices: {e}")
            logger.info("Falling back to mock devices")
            return self._get_mock_devices(organization_id, property_id, integration_id)

    def _get_device_type(self, meross_type: str) -> str:
        """Map Meross device type to our Device types."""
        type_map = {
            "mss110": "PLUG",
            "mss210": "PLUG",
            "mss425e": "SWITCH",
            "mts100": "THERMOSTAT",
            "ms100": "SENSOR",
        }
        return type_map.get(meross_type, "PLUG")

    def _get_mock_devices(
        self,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Return mock Meross devices for testing."""
        return [
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="meross",
                vendor_specific_id="meross_smart_plug_1",
                vendor_name="Meross Smart Plug",
                device_type="PLUG",
                online=True,
                raw_state={"on": True, "power": 12.5, "voltage": 230},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="meross",
                vendor_specific_id="meross_switch_1",
                vendor_name="Meross Smart Switch",
                device_type="SWITCH",
                online=True,
                raw_state={"on": False, "power": 0.0},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

    async def fetch_state(self, device: Device, access_token: str | None = None) -> Device:
        """Refresh device state from Meross API."""
        if not access_token:
            return device

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(
                    f"{MEROSS_API_URL}/homekit/devices/{device.vendor_specific_id}",
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                device_data = data.get("data", {})
                device.online = device_data.get("status") == "online"
                device.raw_state = device_data.get("lastStatus", {})
                device.updated_at = datetime.now(UTC)
        except Exception as e:
            logger.warning(f"Failed to fetch Meross state: {e}")
            device.online = False

        return device

    async def execute(
        self, device: Device, command: str, params: dict[str, Any], access_token: str | None = None
    ) -> bool:
        """Execute control command on Meross device."""
        if not access_token:
            return False

        try:
            nonce = str(int(time.time() * 1000))
            payload_str = ""

            if command == "turn_on":
                payload_str = '{"onoff":1}'
            elif command == "turn_off":
                payload_str = '{"onoff":0}'
            else:
                logger.warning(f"Unknown Meross command: {command}")
                return False

            md5 = hashlib.md5(payload_str.encode()).hexdigest()

            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.post(
                    f"{MEROSS_API_URL}/homekit/devices/{device.vendor_specific_id}/command",
                    json={
                        "nonce": nonce,
                        "payload": payload_str,
                        "md5": md5,
                    },
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("code") == 200
        except Exception as e:
            logger.error(f"Failed to execute Meross command: {e}")
            return False
