"""
eWeLink (Sonoff) API v2 client.

Base URL : https://eu-apia.coolkit.cc   (region-specific; EU shown)
Auth     : Authorization: Bearer {access_token}  (eWeLink OAuth2)
Docs     : https://coolkit-technologies.github.io/eWeLink-API/

eWeLink fronts Sonoff switches and plugs. ``GET /v2/device/thing`` lists the
account's "things"; each thing carries a ``params`` object whose ``switch`` (or
per-channel ``switches``) field is the relay state and whose ``power`` field (on
metering models) is the live draw. Commands are pushed by updating ``params``.

UNTESTED: verify against a real device/account — built from public docs only.
The signed app-login flow that mints the access token is out of scope here.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_BASE_URL = "https://eu-apia.coolkit.cc"
_TIMEOUT = 10.0
_MAX_RETRIES = 3


class EWeLinkAdapter(VendorAdapter):
    """eWeLink (Sonoff) adapter. Requires a valid EWELINK_ACCESS_TOKEN."""

    def __init__(self, access_token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def list_devices(self) -> list[SpireDevice]:
        """GET /v2/device/thing — every device/group on the account."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/v2/device/thing")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("eWeLink list_devices failed: %s", exc)
            return []
        things: list[dict[str, Any]] = data.get("data", {}).get("thingList", [])
        devices: list[SpireDevice] = []
        for thing in things:
            item = thing.get("itemData", thing)
            devices.append(_to_spire(item))
        return devices

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /v2/device/thing/status — live params for one device."""
        params = {"type": 1, "id": device_id, "params": "switch|power|online"}
        # UNTESTED: verify against a real device/account.
        data = await self._request("GET", "/v2/device/thing/status", params=params)
        payload = data.get("data", {})
        payload["deviceid"] = device_id
        return _to_spire(payload)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """POST /v2/device/thing/status — write the relay into the device params."""
        payload = {
            "type": 1,
            "id": device_id,
            "params": _translate_command(command),
        }
        # UNTESTED: verify against a real device/account.
        await self._request("POST", "/v2/device/thing/status", json=payload)
        return True

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
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
                    logger.warning("eWeLink rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("eWeLink API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"eWeLink API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command into an eWeLink params update."""
    action = command.get("action", "")
    if action == "turn_on":
        return {"switch": "on"}
    if action == "turn_off":
        return {"switch": "off"}
    raise ValueError(f"Unsupported command action for eWeLink: {action!r}")


def _read_switch(params: dict[str, Any]) -> bool | None:
    """Read relay state from either the single ``switch`` or first ``switches`` entry."""
    switch = params.get("switch")
    if switch is not None:
        return switch == "on"  # type: ignore[no-any-return]
    switches = params.get("switches")
    if isinstance(switches, list) and switches:
        return switches[0].get("switch") == "on"  # type: ignore[no-any-return]
    return None


def _to_spire(raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw eWeLink device object into a SpireDevice."""
    params: dict[str, Any] = raw.get("params", {})

    state: dict[str, Any] = {}
    switch = _read_switch(params)
    if switch is not None:
        state["on"] = switch

    power_draw: float | None = None
    power = params.get("power")
    if power is not None:
        power_draw = round(float(power), 2)

    online = bool(raw.get("online", True))

    return SpireDevice.from_vendor(
        vendor="ewelink",
        vendor_id=raw.get("deviceid", ""),
        name=raw.get("name", "Sonoff Device"),
        device_type="plug",
        online=online,
        state=state,
        power_draw=power_draw,
        supported_commands=["turn_on", "turn_off"],
    )
