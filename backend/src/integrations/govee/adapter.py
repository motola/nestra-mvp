"""Govee integration adapter."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from property.domain import Device, DeviceType

logger = logging.getLogger(__name__)

GOVEE_API_URL = "https://openapi.api.govee.com/router/api/v1"


class GoveeAdapter:
    """Adapter for Govee smart devices."""

    vendor = "govee"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        api_key: str | None = None,
    ) -> list[Device]:
        """Fetch Govee devices from cloud API."""
        if not api_key:
            logger.warning("No Govee API key provided, returning mock devices")
            return self._get_mock_devices(organization_id, property_id, integration_id)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{GOVEE_API_URL}/device/list", headers={"Govee-Token": api_key}
                )
                response.raise_for_status()
                data = response.json()

                devices = []
                for device_data in data.get("data", {}).get("devices", []):
                    devices.append(
                        Device(
                            id=None,
                            organization_id=organization_id,
                            property_id=property_id,
                            integration_id=integration_id,
                            vendor="govee",
                            vendor_specific_id=device_data.get("deviceId", ""),
                            vendor_name=device_data.get("deviceName", "Govee Device"),
                            device_type=self._get_device_type(device_data.get("deviceType", "")),
                            online=device_data.get("online", False),
                            raw_state=device_data.get("property", {}),
                            last_sync=datetime.now(UTC),
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                        )
                    )

                logger.info(f"Fetched {len(devices)} Govee devices")
                return devices
        except Exception as e:
            logger.error(f"Failed to fetch Govee devices: {e}")
            return self._get_mock_devices(organization_id, property_id, integration_id)

    def _get_device_type(self, govee_type: str) -> DeviceType:
        """Map Govee device type to DeviceType."""
        type_map = {
            "SmartPlug": DeviceType.PLUG,
            "Light": DeviceType.LIGHT,
            "Sensor": DeviceType.SENSOR,
            "Switch": DeviceType.PLUG,
        }
        return type_map.get(govee_type, DeviceType.PLUG)

    def _get_mock_devices(
        self, organization_id: UUID, property_id: UUID, integration_id: UUID
    ) -> list[Device]:
        """Return mock Govee devices for testing."""
        return [
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="govee",
                vendor_specific_id="govee_smart_light_1",
                vendor_name="Govee Smart Light Strip",
                device_type=DeviceType.LIGHT,
                online=True,
                raw_state={"on": True, "brightness": 100, "color": {"r": 255, "g": 100, "b": 50}},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="govee",
                vendor_specific_id="govee_sensor_1",
                vendor_name="Govee Temperature Sensor",
                device_type=DeviceType.SENSOR,
                online=True,
                raw_state={"temperature": 22.5, "humidity": 45},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

    async def fetch_state(self, device: Device, api_key: str | None = None) -> Device:
        """Refresh device state from Govee cloud."""
        if not api_key:
            return device

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{GOVEE_API_URL}/device/state",
                    params={
                        "deviceId": device.vendor_specific_id,
                        "requestId": device.vendor_specific_id,
                    },
                    headers={"Govee-Token": api_key},
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") == 200:
                    device.online = True
                    device.raw_state = data.get("data", {}).get("property", {})
                    device.updated_at = datetime.now(UTC)
        except Exception as e:
            logger.warning(f"Failed to fetch Govee state: {e}")
            device.online = False

        return device

    async def execute(
        self, device: Device, command: str, params: dict[str, Any], api_key: str | None = None
    ) -> bool:
        """Execute command on Govee device."""
        if not api_key:
            return False

        try:
            payload = {
                "requestId": device.vendor_specific_id,
                "payload": {
                    "device": device.vendor_specific_id,
                    "capability": {"type": 1, "instance": "powerSwitch"},
                    "value": 1 if command == "turn_on" else 0,
                },
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{GOVEE_API_URL}/device/control",
                    json=payload,
                    headers={"Govee-Token": api_key},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("code") == 200
        except Exception as e:
            logger.error(f"Failed to execute Govee command: {e}")
            return False
