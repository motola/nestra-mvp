"""
Samsung SmartThings API client.

Base URL : https://api.smartthings.com/v1
Auth     : Authorization: Bearer {personal_access_token}
Docs     : https://developer.smartthings.com/docs/api/public

SmartThings models everything as a "device" with a set of "components", each
carrying "capabilities" (switch, switchLevel, colorControl, temperatureMeasurement,
...). We map those capabilities onto SPIRE traits. State is fetched separately as
the device's full status payload; commands are posted to the device's command
endpoint as capability/command/argument triples.

UNTESTED: verify against a real device/account — built from public docs only.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from spire import SpireDevice, Trait, VendorAdapter, commands_for

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.smartthings.com/v1"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

# SmartThings capability id -> SPIRE trait.
_CAPABILITY_TRAITS: dict[str, Trait] = {
    "switch": Trait.ON_OFF,
    "switchLevel": Trait.DIMMABLE,
    "colorControl": Trait.COLOR,
    "colorTemperature": Trait.COLOR_TEMP,
    "lock": Trait.LOCKABLE,
    "thermostat": Trait.THERMOSTAT,
    "temperatureMeasurement": Trait.REPORTS_TEMPERATURE,
    "relativeHumidityMeasurement": Trait.REPORTS_HUMIDITY,
    "powerMeter": Trait.REPORTS_POWER,
    "motionSensor": Trait.REPORTS_MOTION,
    "contactSensor": Trait.REPORTS_CONTACT,
    "waterSensor": Trait.REPORTS_LEAK,
    "battery": Trait.REPORTS_BATTERY,
    "illuminanceMeasurement": Trait.REPORTS_ILLUMINANCE,
}

# Coarse SPIRE category inferred from the strongest capability present.
_CATEGORY_BY_TRAIT: dict[Trait, str] = {
    Trait.LOCKABLE: "lock",
    Trait.THERMOSTAT: "thermostat",
    Trait.COLOR: "light",
    Trait.COLOR_TEMP: "light",
    Trait.DIMMABLE: "light",
    Trait.ON_OFF: "plug",
}


class SmartThingsAdapter(VendorAdapter):
    """SmartThings adapter. Requires a valid SMARTTHINGS_TOKEN (PAT or OAuth token)."""

    def __init__(self, token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def list_devices(self) -> list[SpireDevice]:
        """GET /devices — every device on the account, with declared capabilities."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/devices")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("SmartThings list_devices failed: %s", exc)
            return []
        raw_devices: list[dict[str, Any]] = data.get("items", [])
        return [_to_spire(d) for d in raw_devices]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /devices/{id} plus /status — metadata merged with live values."""
        # UNTESTED: verify against a real device/account.
        meta = await self._request("GET", f"/devices/{device_id}")
        status = await self._request("GET", f"/devices/{device_id}/status")
        return _to_spire(meta, status)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """POST /devices/{id}/commands — capability/command/argument triples."""
        payload = {"commands": _translate_command(command)}
        # UNTESTED: verify against a real device/account.
        await self._request("POST", f"/devices/{device_id}/commands", json=payload)
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
                    logger.warning("SmartThings rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("SmartThings API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(
            f"SmartThings API unreachable after {_MAX_RETRIES} attempts"
        ) from last_exc


def _translate_command(command: dict[str, Any]) -> list[dict[str, Any]]:
    """Translate an Alphacon command into SmartThings command objects."""
    action = command.get("action", "")
    main = {"component": "main"}
    if action == "turn_on":
        return [{**main, "capability": "switch", "command": "on"}]
    if action == "turn_off":
        return [{**main, "capability": "switch", "command": "off"}]
    if action == "set_brightness":
        return [
            {
                **main,
                "capability": "switchLevel",
                "command": "setLevel",
                "arguments": [int(command.get("value", 100))],
            }
        ]
    if action == "lock":
        return [{**main, "capability": "lock", "command": "lock"}]
    if action == "unlock":
        return [{**main, "capability": "lock", "command": "unlock"}]
    raise ValueError(f"Unsupported command action for SmartThings: {action!r}")


def _capabilities(raw: dict[str, Any]) -> list[str]:
    """Collect capability ids across all of a device's components."""
    caps: list[str] = []
    for component in raw.get("components", []):
        for cap in component.get("capabilities", []):
            cap_id = cap.get("id")
            if cap_id:
                caps.append(cap_id)
    return caps


def _traits_for(capabilities: list[str]) -> list[Trait]:
    """Map declared capabilities onto SPIRE traits, de-duplicated and order-stable."""
    traits: list[Trait] = []
    for cap in capabilities:
        trait = _CAPABILITY_TRAITS.get(cap)
        if trait is not None and trait not in traits:
            traits.append(trait)
    return traits


def _infer_type(traits: list[Trait]) -> str:
    """Pick the coarse device type from the strongest actuator trait present."""
    for trait, category in _CATEGORY_BY_TRAIT.items():
        if trait in traits:
            return category
    return "sensor" if traits else "other"


def _read_state(status: dict[str, Any] | None) -> dict[str, Any]:
    """Pull live values out of a SmartThings status payload (main component)."""
    state: dict[str, Any] = {}
    if not status:
        return state
    main = status.get("components", {}).get("main", {})
    switch = main.get("switch", {}).get("switch", {}).get("value")
    if switch is not None:
        state["on"] = switch == "on"
    level = main.get("switchLevel", {}).get("level", {}).get("value")
    if level is not None:
        state["brightness"] = int(level)
    temp = main.get("temperatureMeasurement", {}).get("temperature", {}).get("value")
    if temp is not None:
        state["temperature"] = float(temp)
    humidity = main.get("relativeHumidityMeasurement", {}).get("humidity", {}).get("value")
    if humidity is not None:
        state["humidity"] = float(humidity)
    return state


def _to_spire(raw: dict[str, Any], status: dict[str, Any] | None = None) -> SpireDevice:
    """Convert a raw SmartThings device (plus optional status) into a SpireDevice."""
    capabilities = _capabilities(raw)
    traits = _traits_for(capabilities)
    return SpireDevice.from_vendor(
        vendor="smartthings",
        vendor_id=raw.get("deviceId", ""),
        name=raw.get("label") or raw.get("name", "SmartThings Device"),
        device_type=_infer_type(traits),
        online=raw.get("healthState", {}).get("state", "ONLINE") == "ONLINE",
        state=_read_state(status),
        supported_commands=commands_for(traits),
        traits=traits,
    )
