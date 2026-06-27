"""VendorAdapter wrapper around the local Shelly controller.

Local Shelly devices are addressed by IP, so the adapter is constructed with a
``{device_id: ip}`` map (the caller builds it from the device registry). This
keeps the adapter free of any database/persistence coupling while still
presenting the standard vendor-agnostic contract.
"""

from __future__ import annotations

import logging
from typing import Any

from integrations.shelly_local.client import ShellyLocalController
from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_DEFAULT_NAME = "Shelly"
_SUPPORTED_COMMANDS = ["turn_on", "turn_off"]


class ShellyLocalAdapter(VendorAdapter):
    def __init__(self, devices: dict[str, str], names: dict[str, str] | None = None) -> None:
        self._ips = devices
        self._names = names or {}

    def _name(self, device_id: str) -> str:
        return self._names.get(device_id, _DEFAULT_NAME)

    async def list_devices(self) -> list[SpireDevice]:
        result: list[SpireDevice] = []
        for device_id, ip in self._ips.items():
            try:
                result.append(await self.get_device_state(device_id))
            except Exception as exc:
                logger.warning("Shelly device %s (%s) unreachable: %s", device_id, ip, exc)
                result.append(
                    offline_device(device_id=device_id, vendor_id=ip, name=self._name(device_id))
                )
        return result

    async def get_device_state(self, device_id: str) -> SpireDevice:
        ip = self._ips[device_id]
        state = await ShellyLocalController(ip).get_state()
        return to_spire_device(
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


def to_spire_device(
    *,
    device_id: str,
    vendor_id: str,
    name: str,
    state: dict[str, Any],
) -> SpireDevice:
    """Build a SpireDevice from a ShellyLocalController.get_state() result."""
    power = float(state["power"]) if state.get("power") is not None else None
    return SpireDevice.from_vendor(
        vendor="shelly",
        vendor_id=vendor_id,
        name=name,
        device_type="plug",
        online=True,
        state={"on": bool(state.get("on", False)), "power": float(state.get("power", 0.0))},
        power_draw=power,
        supported_commands=list(_SUPPORTED_COMMANDS),
    )


def offline_device(*, device_id: str, vendor_id: str, name: str) -> SpireDevice:
    """Represent an unreachable Shelly device as offline."""
    return SpireDevice.from_vendor(
        vendor="shelly",
        vendor_id=vendor_id,
        name=name,
        device_type="plug",
        online=False,
        supported_commands=list(_SUPPORTED_COMMANDS),
    )
