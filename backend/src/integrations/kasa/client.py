"""
TP-Link Kasa Cloud API client.

Base URL : https://wap.tplinkcloud.com
Auth     : a ``token`` obtained from a login call, passed as a query parameter.
Docs     : reverse-engineered community API (TP-Link has no official public docs);
           see https://github.com/python-kasa/python-kasa for the protocol shape.

The Kasa cloud works by "passthrough": you POST a ``passthrough`` request whose
``requestData`` is a JSON string of the device's native command (e.g.
``{"system":{"get_sysinfo":{}}}``). We list devices via ``getDeviceList`` and
control plugs/switches through the relay ``set_relay_state`` command.

UNTESTED: verify against a real device/account — built from community docs only.
The passthrough requestData must be a JSON-encoded string, not a nested object.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx

from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_BASE_URL = "https://wap.tplinkcloud.com"
_TIMEOUT = 10.0
_MAX_RETRIES = 3


class KasaAdapter(VendorAdapter):
    """TP-Link Kasa cloud adapter. Requires a valid KASA_TOKEN."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._headers = {"Content-Type": "application/json"}

    async def list_devices(self) -> list[SpireDevice]:
        """POST getDeviceList — every device bound to the Kasa cloud account."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request({"method": "getDeviceList"})
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("Kasa list_devices failed: %s", exc)
            return []
        raw_devices: list[dict[str, Any]] = data.get("result", {}).get("deviceList", [])
        return [_to_spire(d) for d in raw_devices]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """Passthrough get_sysinfo to the device, merged onto its list metadata."""
        request: dict[str, Any] = {
            "system": {"get_sysinfo": {}},
            "emeter": {"get_realtime": {}},
        }
        # UNTESTED: verify against a real device/account.
        data = await self._passthrough(device_id, request)
        sysinfo = data.get("system", {}).get("get_sysinfo", {})
        emeter = data.get("emeter", {}).get("get_realtime", {})
        sysinfo["deviceId"] = device_id
        return _to_spire(sysinfo, emeter)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """Passthrough a relay state change to the device."""
        request = _translate_command(command)
        # UNTESTED: verify against a real device/account.
        await self._passthrough(device_id, request)
        return True

    async def _passthrough(self, device_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """Wrap a native device request in a Kasa cloud passthrough envelope."""
        envelope = {
            "method": "passthrough",
            "params": {"deviceId": device_id, "requestData": json.dumps(request)},
        }
        data = await self._request(envelope)
        response_data = data.get("result", {}).get("responseData", "{}")
        if isinstance(response_data, str):
            return json.loads(response_data)  # type: ignore[no-any-return]
        return response_data  # type: ignore[no-any-return]

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST to the cloud root with the token as a query param, with backoff."""
        url = f"{_BASE_URL}/?token={self._token}"
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    r = await client.post(url, headers=self._headers, json=payload)
                    r.raise_for_status()
                    return r.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("Kasa rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("Kasa API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"Kasa API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command into a Kasa native relay request."""
    action = command.get("action", "")
    if action == "turn_on":
        return {"system": {"set_relay_state": {"state": 1}}}
    if action == "turn_off":
        return {"system": {"set_relay_state": {"state": 0}}}
    raise ValueError(f"Unsupported command action for Kasa: {action!r}")


def _to_spire(raw: dict[str, Any], emeter: dict[str, Any] | None = None) -> SpireDevice:
    """Convert a raw Kasa device object (sysinfo + optional emeter) into a SpireDevice."""
    state: dict[str, Any] = {}
    relay = raw.get("relay_state")
    if relay is not None:
        state["on"] = bool(relay)

    power_draw: float | None = None
    if emeter:
        # Newer firmware reports milliwatts (``power_mw``); older reports watts.
        if "power_mw" in emeter:
            power_draw = round(int(emeter["power_mw"]) / 1000, 2)
        elif "power" in emeter:
            power_draw = round(float(emeter["power"]), 2)

    # ``status``: 1 == online in the cloud device list.
    online = raw.get("status", 1) == 1 if "status" in raw else True

    return SpireDevice.from_vendor(
        vendor="kasa",
        vendor_id=raw.get("deviceId", ""),
        name=raw.get("alias") or raw.get("deviceName", "Kasa Device"),
        device_type="plug",
        online=online,
        state=state,
        power_draw=power_draw,
        supported_commands=["turn_on", "turn_off"],
    )
