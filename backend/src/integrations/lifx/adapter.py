"""LIFX integration adapter."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from property.domain import Device, DeviceType

logger = logging.getLogger(__name__)

LIFX_API_URL = "https://api.lifx.com/v1"


class LifxAdapter:
    """Adapter for LIFX smart lights."""

    vendor = "lifx"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        portfolio_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        api_token: str | None = None,
    ) -> list[Device]:
        """Fetch LIFX devices from cloud API."""
        if not api_token:
            logger.warning("No LIFX API token provided, returning mock devices")
            return self._get_mock_devices(organization_id, portfolio_id, property_id, integration_id)

        try:
            async with httpx.AsyncClient(
                timeout=10.0, headers={"Authorization": f"Bearer {api_token}"}
            ) as client:
                response = await client.get(f"{LIFX_API_URL}/lights")
                response.raise_for_status()
                devices = []
                for light in response.json():
                    color = light.get("color", {})
                    devices.append(
                        Device(
                            id=None,
                            organization_id=organization_id,
                            portfolio_id=portfolio_id,
                            property_id=property_id,
                            integration_id=integration_id,
                            vendor="lifx",
                            vendor_specific_id=light.get("id", ""),
                            vendor_name=light.get("label", "LIFX Light"),
                            device_type=DeviceType.LIGHT,
                            online=light.get("connected", False),
                            raw_state={
                                "on": light.get("power", "off") == "on",
                                "brightness": light.get("brightness", 0),
                                "color": {
                                    k: color.get(k, 0) for k in ["hue", "saturation", "kelvin"]
                                },
                                "group": light.get("group", {}).get("name", ""),
                            },
                            last_sync=datetime.now(UTC),
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                        )
                    )
                logger.info(f"Fetched {len(devices)} LIFX devices")
                return devices
        except Exception as e:
            logger.error(f"Failed to fetch LIFX devices: {e}")
            return self._get_mock_devices(organization_id, portfolio_id, property_id, integration_id)

    def _get_mock_devices(
        self, organization_id: UUID, portfolio_id: UUID, property_id: UUID, integration_id: UUID
    ) -> list[Device]:
        """Return mock LIFX devices for testing."""
        return [
            Device(
                id=None,
                organization_id=organization_id,
                portfolio_id=portfolio_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="lifx",
                vendor_specific_id="lifx_light_1",
                vendor_name="LIFX A19",
                device_type=DeviceType.LIGHT,
                online=True,
                raw_state={
                    "on": True,
                    "brightness": 80,
                    "color": {"hue": 45, "saturation": 100, "kelvin": 3000},
                },
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="lifx",
                vendor_specific_id="lifx_light_2",
                vendor_name="LIFX BR30",
                device_type=DeviceType.LIGHT,
                online=True,
                raw_state={
                    "on": False,
                    "brightness": 0,
                    "color": {"hue": 0, "saturation": 0, "kelvin": 2700},
                },
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

    async def fetch_state(self, device: Device, api_token: str | None = None) -> Device:
        """Refresh device state from LIFX cloud."""
        if not api_token:
            return device
        try:
            async with httpx.AsyncClient(
                timeout=10.0, headers={"Authorization": f"Bearer {api_token}"}
            ) as client:
                response = await client.get(f"{LIFX_API_URL}/lights/id:{device.vendor_specific_id}")
                light = response.json()[0]
                color = light.get("color", {})
                device.online = light.get("connected", False)
                device.raw_state = {
                    "on": light.get("power", "off") == "on",
                    "brightness": light.get("brightness", 0),
                    "color": {k: color.get(k, 0) for k in ["hue", "saturation", "kelvin"]},
                }
                device.updated_at = datetime.now(UTC)
        except Exception as e:
            logger.warning(f"Failed to fetch LIFX state: {e}")
            device.online = False
        return device

    async def execute(
        self, device: Device, command: str, params: dict[str, Any], api_token: str | None = None
    ) -> bool:
        """Execute command on LIFX device."""
        if not api_token:
            return False
        try:
            selector = f"id:{device.vendor_specific_id}"
            async with httpx.AsyncClient(
                timeout=10.0, headers={"Authorization": f"Bearer {api_token}"}
            ) as client:
                if command == "turn_on":
                    await client.post(f"{LIFX_API_URL}/lights/{selector}/turn/on")
                    return True
                elif command == "turn_off":
                    await client.post(f"{LIFX_API_URL}/lights/{selector}/turn/off")
                    return True
                elif command == "set_brightness":
                    await client.post(
                        f"{LIFX_API_URL}/lights/{selector}/state",
                        json={"brightness": params.get("brightness", 0.5)},
                    )
                    return True
        except Exception as e:
            logger.error(f"Failed to execute LIFX command: {e}")
        return False
