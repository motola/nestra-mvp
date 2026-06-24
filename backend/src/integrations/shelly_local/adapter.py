"""BaseVendorAdapter wrapper around the local Shelly controller.

Local Shelly devices are addressed by IP, so the adapter is constructed with a
``{device_id: ip}`` map (the caller builds it from the device registry). This
keeps the adapter free of any database/persistence coupling while still
presenting the standard vendor-agnostic contract.
"""

from __future__ import annotations

import logging
from typing import Any

from integrations import BaseVendorAdapter
from integrations.shelly_local.controller import ShellyLocalController
from integrations.shelly_local.normaliser import offline_device, to_alphacon_device
from models.device import AlphaconDevice

logger = logging.getLogger(__name__)

_DEFAULT_NAME = "Shelly"


class ShellyLocalAdapter(BaseVendorAdapter):
    def __init__(self, devices: dict[str, str], names: dict[str, str] | None = None) -> None:
        self._ips = devices
        self._names = names or {}

    def _name(self, device_id: str) -> str:
        return self._names.get(device_id, _DEFAULT_NAME)

    async def list_devices(self) -> list[AlphaconDevice]:
        result: list[AlphaconDevice] = []
        for device_id, ip in self._ips.items():
            try:
                result.append(await self.get_device_state(device_id))
            except Exception as exc:
                logger.warning("Shelly device %s (%s) unreachable: %s", device_id, ip, exc)
                result.append(
                    offline_device(device_id=device_id, vendor_id=ip, name=self._name(device_id))
                )
        return result

    async def get_device_state(self, device_id: str) -> AlphaconDevice:
        ip = self._ips[device_id]
        state = await ShellyLocalController(ip).get_state()
        return to_alphacon_device(
            device_id=device_id, vendor_id=ip, name=self._name(device_id), state=state
        )

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        ip = self._ips[device_id]
        controller = ShellyLocalController(ip)
        action = command.get("action")
        if action == "turn_on":
            return await controller.turn_on()
        if action == "turn_off":
            return await controller.turn_off()
        logger.warning("Shelly adapter received unsupported command: %r", action)
        return False
