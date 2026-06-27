"""
LIFX Cloud API client.

Base URL : https://api.lifx.com/v1
Auth     : Authorization: Bearer {LIFX_API_TOKEN}
Docs     : https://api.lifx.com/

Phase 1 — implemented for cloud polling. No local LAN protocol.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from integrations import BaseVendorAdapter
from integrations.lifx.normaliser import normalise_device
from spire import SpireDevice

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.lifx.com/v1"
_TIMEOUT = 10.0
_MAX_RETRIES = 3


class LIFXAdapter(BaseVendorAdapter):
    """LIFX Cloud API adapter. Requires a valid LIFX_API_TOKEN."""

    def __init__(self, api_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {api_token}"}

    async def list_devices(self) -> list[SpireDevice]:
        """GET /lights/all — returns every light on the account."""
        data = await self._request("GET", "/lights/all")
        if not isinstance(data, list):
            return []
        return [normalise_device(d) for d in data]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /lights/id:{device_id} — returns state for a single light."""
        data = await self._request("GET", f"/lights/id:{device_id}")
        if isinstance(data, list) and data:
            return normalise_device(data[0])
        raise ValueError(f"LIFX device not found: {device_id}")

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """PUT /lights/id:{device_id}/state — set power, brightness, colour."""
        payload = _translate_command(command)
        await self._request("PUT", f"/lights/id:{device_id}/state", json=payload)
        return True

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        url = f"{_BASE_URL}{path}"
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    r = await client.request(method, url, headers=self._headers, **kwargs)
                    r.raise_for_status()
                    return r.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("LIFX rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("LIFX API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"LIFX API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate Alphacon command into LIFX state payload."""
    action = command.get("action", "")
    if action == "turn_on":
        return {"power": "on"}
    if action == "turn_off":
        return {"power": "off"}
    if action == "set_brightness":
        return {"brightness": float(command.get("value", 1.0)) / 100}
    if action == "set_color":
        r = command.get("r", 255)
        g = command.get("g", 255)
        b = command.get("b", 255)
        return {"color": f"rgb:{r},{g},{b}"}
    raise ValueError(f"Unsupported command action for LIFX: {action!r}")
