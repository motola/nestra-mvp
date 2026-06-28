"""
ecobee API client.

Base URL : https://api.ecobee.com/1
Auth     : Authorization: Bearer {access_token}  (ecobee OAuth2)
Docs     : https://www.ecobee.com/home/developer/api/documentation/v1/

ecobee exposes thermostats through a ``GET /thermostat`` call that takes a JSON
``selection`` body describing what to include (runtime, settings). Temperatures
are returned in tenths of a degree Fahrenheit; we convert to Celsius for SPIRE's
``temperature`` / ``target_temperature`` state keys.

UNTESTED: verify against a real device/account — built from public docs only.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx

from spire import SpireDevice, Trait, VendorAdapter, commands_for

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.ecobee.com/1"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

_THERMOSTAT_TRAITS = (
    Trait.THERMOSTAT,
    Trait.REPORTS_TEMPERATURE,
    Trait.REPORTS_HUMIDITY,
)


class EcobeeAdapter(VendorAdapter):
    """ecobee adapter. Requires a valid ECOBEE_ACCESS_TOKEN."""

    def __init__(self, access_token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def list_devices(self) -> list[SpireDevice]:
        """GET /thermostat with a selection asking for runtime + settings."""
        selection = {
            "selection": {
                "selectionType": "registered",
                "selectionMatch": "",
                "includeRuntime": True,
                "includeSettings": True,
            }
        }
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/thermostat", params={"json": json.dumps(selection)})
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("ecobee list_devices failed: %s", exc)
            return []
        raw_thermostats: list[dict[str, Any]] = data.get("thermostatList", [])
        return [_to_spire(t) for t in raw_thermostats]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /thermostat filtered to one identifier."""
        selection = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": device_id,
                "includeRuntime": True,
                "includeSettings": True,
            }
        }
        # UNTESTED: verify against a real device/account.
        data = await self._request("GET", "/thermostat", params={"json": json.dumps(selection)})
        items: list[dict[str, Any]] = data.get("thermostatList", [])
        if not items:
            raise ValueError(f"ecobee thermostat not found: {device_id}")
        return _to_spire(items[0])

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """POST /thermostat — a setHold function to push a target temperature."""
        payload = _translate_command(device_id, command)
        # UNTESTED: verify against a real device/account.
        await self._request("POST", "/thermostat", json=payload)
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
                    logger.warning("ecobee rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("ecobee API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"ecobee API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _f_tenths_to_celsius(value: int) -> float:
    """ecobee reports tenths of a degree Fahrenheit; convert to Celsius."""
    fahrenheit = value / 10
    return round((fahrenheit - 32) * 5 / 9, 1)


def _celsius_to_f_tenths(celsius: float) -> int:
    """Convert a Celsius target into ecobee's tenths-of-Fahrenheit unit."""
    return round((celsius * 9 / 5 + 32) * 10)


def _translate_command(device_id: str, command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command into an ecobee thermostat update."""
    action = command.get("action", "")
    if action == "set_target_temperature":
        target = _celsius_to_f_tenths(float(command.get("value", 21.0)))
        return {
            "selection": {"selectionType": "thermostats", "selectionMatch": device_id},
            "functions": [
                {
                    "type": "setHold",
                    "params": {
                        "holdType": "nextTransition",
                        "heatHoldTemp": target,
                        "coolHoldTemp": target,
                    },
                }
            ],
        }
    raise ValueError(f"Unsupported command action for ecobee: {action!r}")


def _to_spire(raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw ecobee thermostat object into a SpireDevice."""
    runtime: dict[str, Any] = raw.get("runtime", {})

    state: dict[str, Any] = {}
    actual_temp = runtime.get("actualTemperature")
    if actual_temp is not None:
        state["temperature"] = _f_tenths_to_celsius(int(actual_temp))
    humidity = runtime.get("actualHumidity")
    if humidity is not None:
        state["humidity"] = float(humidity)
    desired = runtime.get("desiredHeat")
    if desired is not None:
        state["target_temperature"] = _f_tenths_to_celsius(int(desired))

    return SpireDevice.from_vendor(
        vendor="ecobee",
        vendor_id=str(raw.get("identifier", "")),
        name=raw.get("name", "ecobee Thermostat"),
        device_type="thermostat",
        online=bool(raw.get("isRegistered", True)),
        state=state,
        supported_commands=commands_for(list(_THERMOSTAT_TRAITS)),
        traits=list(_THERMOSTAT_TRAITS),
    )
