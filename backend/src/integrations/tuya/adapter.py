"""
Tuya Cloud (OpenAPI) client.

Base URL : https://openapi.tuyaus.com   (region-specific; US shown)
Auth     : HMAC-SHA256 signed requests using client_id + client_secret, which
           yield a short-lived access_token used on subsequent calls.
Docs     : https://developer.tuya.com/en/docs/cloud/

Tuya is a broad ecosystem: plugs, lights, and sensors all surface as "devices"
with a category code and a list of "status" datapoints (codes like ``switch_1``,
``bright_value``, ``temp_current``). We infer a SPIRE type from the category and
map status codes onto traits/state.

UNTESTED: verify against a real device/account — built from public docs only.
Signing here follows the documented v2 scheme but the exact string-to-sign and
token lifecycle must be confirmed against a live Tuya project.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any

import httpx

from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_BASE_URL = "https://openapi.tuyaus.com"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

# Tuya category code prefixes -> SPIRE device type.
_CATEGORY_TYPE_MAP: dict[str, str] = {
    "dj": "light",  # light source
    "dd": "light",  # light strip
    "xdd": "light",  # ceiling light
    "cz": "plug",  # socket
    "pc": "plug",  # power strip
    "kg": "plug",  # switch
    "wsdcg": "sensor",  # temp/humidity sensor
    "mcs": "sensor",  # contact sensor
    "pir": "sensor",  # motion sensor
    "sj": "sensor",  # water leak sensor
}


class TuyaAdapter(VendorAdapter):
    """Tuya Cloud adapter. Requires TUYA_ACCESS_ID and TUYA_ACCESS_SECRET."""

    def __init__(self, access_id: str, access_secret: str = "") -> None:
        # access_secret may be packed as "id:secret" when only one settings field
        # is available; accept both shapes so the registry can pass a single value.
        if not access_secret and ":" in access_id:
            access_id, access_secret = access_id.split(":", 1)
        self._access_id = access_id
        self._access_secret = access_secret
        self._token: str = ""

    async def list_devices(self) -> list[SpireDevice]:
        """GET /v1.0/users/{uid}/devices is account-scoped; we use the app device list."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/v1.0/iot-01/associated-users/devices")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("Tuya list_devices failed: %s", exc)
            return []
        result = data.get("result", {})
        if isinstance(result, dict):
            raw_devices: list[dict[str, Any]] = result.get("devices", [])
        else:
            raw_devices = result
        return [_to_spire(d) for d in raw_devices]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /v1.0/devices/{id} — metadata plus the current status datapoints."""
        # UNTESTED: verify against a real device/account.
        data = await self._request("GET", f"/v1.0/devices/{device_id}")
        return _to_spire(data.get("result", {}))

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """POST /v1.0/devices/{id}/commands — list of {code, value} datapoints."""
        payload = {"commands": _translate_command(command)}
        # UNTESTED: verify against a real device/account.
        await self._request("POST", f"/v1.0/devices/{device_id}/commands", json=payload)
        return True

    async def _ensure_token(self, client: httpx.AsyncClient) -> None:
        """Fetch and cache an access token using a token-mode signed request."""
        if self._token:
            return
        path = "/v1.0/token?grant_type=1"
        headers = self._sign(path, "GET", "", token="")
        r = await client.get(f"{_BASE_URL}{path}", headers=headers)
        r.raise_for_status()
        self._token = r.json().get("result", {}).get("access_token", "")

    def _sign(self, path: str, method: str, body: str, *, token: str) -> dict[str, str]:
        """Build the Tuya v2 signature headers for one request."""
        t = str(int(time.time() * 1000))
        content_hash = hashlib.sha256(body.encode()).hexdigest()
        string_to_sign = f"{method}\n{content_hash}\n\n{path}"
        message = f"{self._access_id}{token}{t}{string_to_sign}"
        signature = (
            hmac.new(self._access_secret.encode(), message.encode(), hashlib.sha256)
            .hexdigest()
            .upper()
        )
        headers = {
            "client_id": self._access_id,
            "sign": signature,
            "t": t,
            "sign_method": "HMAC-SHA256",
            "Content-Type": "application/json",
        }
        if token:
            headers["access_token"] = token
        return headers

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Signed HTTP request with token bootstrap and backoff on errors."""
        last_exc: Exception | None = None
        body = ""
        json_body = kwargs.get("json")
        if json_body is not None:
            body = json.dumps(json_body)

        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    await self._ensure_token(client)
                    headers = self._sign(path, method, body, token=self._token)
                    r = await client.request(
                        method, f"{_BASE_URL}{path}", headers=headers, **kwargs
                    )
                    r.raise_for_status()
                    return r.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("Tuya rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("Tuya API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"Tuya API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> list[dict[str, Any]]:
    """Translate an Alphacon command into Tuya datapoint commands."""
    action = command.get("action", "")
    if action == "turn_on":
        return [{"code": "switch_1", "value": True}]
    if action == "turn_off":
        return [{"code": "switch_1", "value": False}]
    if action == "set_brightness":
        # Tuya brightness is typically 10..1000; scale a 0..100 percent into that range.
        pct = int(command.get("value", 100))
        return [{"code": "bright_value_v2", "value": max(10, round(pct * 10))}]
    raise ValueError(f"Unsupported command action for Tuya: {action!r}")


def _infer_type(category: str) -> str:
    """Infer SPIRE device type from a Tuya category code."""
    return _CATEGORY_TYPE_MAP.get(category, "other")


def _status_map(status: list[dict[str, Any]]) -> dict[str, Any]:
    """Flatten Tuya's status list of {code, value} into a single dict."""
    result: dict[str, Any] = {}
    for item in status:
        code = item.get("code")
        if isinstance(code, str):
            result[code] = item.get("value")
    return result


def _to_spire(raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw Tuya device object into a SpireDevice."""
    category: str = raw.get("category", "")
    device_type = _infer_type(category)
    status = _status_map(raw.get("status", []))

    state: dict[str, Any] = {}
    if "switch_1" in status:
        state["on"] = bool(status["switch_1"])
    elif "switch" in status:
        state["on"] = bool(status["switch"])
    if "bright_value_v2" in status:
        state["brightness"] = round(int(status["bright_value_v2"]) / 10)
    if "temp_current" in status:
        state["temperature"] = float(status["temp_current"]) / 10
    if "humidity_value" in status:
        state["humidity"] = float(status["humidity_value"])

    commands = ["turn_on", "turn_off"] if device_type in ("light", "plug") else []
    if device_type == "light" and "bright_value_v2" in status:
        commands.append("set_brightness")

    return SpireDevice.from_vendor(
        vendor="tuya",
        vendor_id=raw.get("id", ""),
        name=raw.get("name", "Tuya Device"),
        device_type=device_type,
        online=bool(raw.get("online", False)),
        state=state,
        supported_commands=commands,
    )
