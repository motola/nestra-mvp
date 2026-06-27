"""
Govee Cloud API client.

Base URL : https://developer-api.govee.com/v1
Auth     : Govee-API-Key header
Rate limit: 100 requests / minute (enforced via retry + backoff)

Known issue: device state does not sync correctly when the Govee phone app
is actively connected via Bluetooth. The API reflects cloud state, which
lags behind BLE state. This is a Govee platform limitation — no workaround.

Poll interval for Phase 1: 30 seconds (enforced by device_service.py).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from integrations import BaseVendorAdapter
from integrations.govee.normaliser import normalise_device, normalise_state
from spire import SpireDevice

logger = logging.getLogger(__name__)

_BASE_URL = "https://developer-api.govee.com/v1"
_TIMEOUT = 10.0
_MAX_RETRIES = 3


class GoveeAdapter(BaseVendorAdapter):
    """Govee Cloud API adapter. Requires a valid GOVEE_API_KEY."""

    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Govee-API-Key": api_key,
            "Content-Type": "application/json",
        }

    async def list_devices(self) -> list[SpireDevice]:
        """GET /devices — returns all devices registered to the account."""
        data = await self._request("GET", "/devices")
        raw_devices: list[dict[str, Any]] = data.get("data", {}).get("devices", [])
        return [normalise_device(d) for d in raw_devices]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """
        GET /devices/state — returns current state for a single device.

        device_id is the Govee device MAC address (vendor_id), not the Alphacon UUID.
        The caller must pass vendor_id here, not the Alphacon id.
        """
        # We need both device MAC and model — stored together as "mac::model"
        parts = device_id.split("::", 1)
        if len(parts) != 2:
            raise ValueError(f"Govee device_id must be 'mac::model', got: {device_id!r}")
        mac, model = parts
        data = await self._request("GET", "/devices/state", params={"device": mac, "model": model})
        return normalise_state(data.get("data", {}))

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """
        PUT /devices/control — sends a command to a single device.

        command uses Alphacon keys:
            {"action": "turn_on"}
            {"action": "turn_off"}
            {"action": "set_brightness", "value": 0-100}
            {"action": "set_color", "r": 0-255, "g": 0-255, "b": 0-255}
        """
        parts = device_id.split("::", 1)
        if len(parts) != 2:
            raise ValueError(f"Govee device_id must be 'mac::model', got: {device_id!r}")
        mac, model = parts
        govee_cmd = _translate_command(command)
        payload = {"device": mac, "model": model, "cmd": govee_cmd}
        await self._request("PUT", "/devices/control", json=payload)
        return True

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """HTTP request with exponential backoff on 429 / network errors."""
        url = f"{_BASE_URL}{path}"
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    r = await client.request(method, url, headers=self._headers, **kwargs)
                    r.raise_for_status()
                    return r.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("Govee rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error(
                        "Govee API error %s: %s",
                        exc.response.status_code,
                        exc.response.text,
                    )
                    raise
            except httpx.HTTPError as exc:
                wait = 2**attempt
                logger.warning("Govee network error (attempt %s): %s", attempt + 1, exc)
                await asyncio.sleep(wait)
                last_exc = exc

        raise RuntimeError(f"Govee API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command dict into a Govee cmd object."""
    action = command.get("action", "")
    if action == "turn_on":
        return {"name": "turn", "value": "on"}
    if action == "turn_off":
        return {"name": "turn", "value": "off"}
    if action == "set_brightness":
        return {"name": "brightness", "value": int(command.get("value", 100))}
    if action == "set_color":
        return {
            "name": "color",
            "value": {
                "r": int(command.get("r", 255)),
                "g": int(command.get("g", 255)),
                "b": int(command.get("b", 255)),
            },
        }
    raise ValueError(f"Unsupported command action for Govee: {action!r}")
