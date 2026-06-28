"""
Philips Hue Cloud API (v2) client.

Base URL : https://api.meethue.com/route/clip/v2
Auth     : Authorization: Bearer {access_token}  (Hue remote OAuth2 token)
Docs     : https://developers.meethue.com/develop/hue-api-v2/

The Hue v2 CLIP API models a bridge as a graph of "resources". A controllable
bulb surfaces as a ``light`` resource whose ``id`` we use as the vendor id.
Power and brightness live on the same resource; colour is a nested ``color``
object using CIE xy plus a ``color_temperature`` (mirek) object.

UNTESTED: verify against a real device/account — built from public docs only.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.meethue.com/route/clip/v2"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

# Mirek is the reciprocal megakelvin unit Hue uses for colour temperature.
_MIREK_SCALE = 1_000_000


class HueAdapter(VendorAdapter):
    """Philips Hue remote-API adapter. Requires a valid HUE_API_KEY (OAuth token)."""

    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def list_devices(self) -> list[SpireDevice]:
        """GET /resource/light — every light resource the bridge exposes."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/resource/light")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("Hue list_devices failed: %s", exc)
            return []
        raw_lights: list[dict[str, Any]] = data.get("data", [])
        return [_to_spire(light) for light in raw_lights]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /resource/light/{id} — current state for one light."""
        # UNTESTED: verify against a real device/account.
        data = await self._request("GET", f"/resource/light/{device_id}")
        items: list[dict[str, Any]] = data.get("data", [])
        if not items:
            raise ValueError(f"Hue light not found: {device_id}")
        return _to_spire(items[0])

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """PUT /resource/light/{id} — set power, brightness, or colour."""
        payload = _translate_command(command)
        # UNTESTED: verify against a real device/account.
        await self._request("PUT", f"/resource/light/{device_id}", json=payload)
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
                    logger.warning("Hue rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("Hue API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"Hue API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command into a Hue v2 light payload."""
    action = command.get("action", "")
    if action == "turn_on":
        return {"on": {"on": True}}
    if action == "turn_off":
        return {"on": {"on": False}}
    if action == "set_brightness":
        return {"dimming": {"brightness": float(command.get("value", 100))}}
    if action == "set_color_temp":
        kelvin = int(command.get("value", 3500))
        return {"color_temperature": {"mirek": round(_MIREK_SCALE / max(kelvin, 1))}}
    if action == "set_color":
        x, y = _rgb_to_xy(
            int(command.get("r", 255)),
            int(command.get("g", 255)),
            int(command.get("b", 255)),
        )
        return {"color": {"xy": {"x": x, "y": y}}}
    raise ValueError(f"Unsupported command action for Hue: {action!r}")


def _rgb_to_xy(r: int, g: int, b: int) -> tuple[float, float]:
    """Convert 8-bit sRGB to CIE 1931 xy (the colour space the Hue API expects)."""
    rf, gf, bf = r / 255, g / 255, b / 255
    big_x = rf * 0.4124 + gf * 0.3576 + bf * 0.1805
    big_y = rf * 0.2126 + gf * 0.7152 + bf * 0.0722
    big_z = rf * 0.0193 + gf * 0.1192 + bf * 0.9505
    total = big_x + big_y + big_z
    if total == 0:
        return 0.0, 0.0
    return round(big_x / total, 4), round(big_y / total, 4)


def _to_spire(raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw Hue v2 light resource into a SpireDevice."""
    metadata: dict[str, Any] = raw.get("metadata", {})
    on_obj: dict[str, Any] = raw.get("on", {})
    dimming: dict[str, Any] = raw.get("dimming", {})

    state: dict[str, Any] = {"on": bool(on_obj.get("on", False))}
    if "brightness" in dimming:
        state["brightness"] = round(float(dimming["brightness"]))

    color_temp = raw.get("color_temperature", {})
    mirek = color_temp.get("mirek")
    if mirek:
        state["color_temp_kelvin"] = round(_MIREK_SCALE / int(mirek))

    commands = ["turn_on", "turn_off"]
    if dimming:
        commands.append("set_brightness")
    if "color_temperature" in raw:
        commands.append("set_color_temp")
    if "color" in raw:
        commands.append("set_color")

    return SpireDevice.from_vendor(
        vendor="hue",
        vendor_id=raw.get("id", ""),
        name=metadata.get("name", "Hue Light"),
        device_type="light",
        online=True,
        state=state,
        supported_commands=commands,
    )
