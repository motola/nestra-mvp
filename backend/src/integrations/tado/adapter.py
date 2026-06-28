"""
tado° API client.

Base URL : https://my.tado.com/api/v2
Auth     : Authorization: Bearer {access_token}  (tado OAuth2)
Docs     : https://shkspr.mobi/blog/2019/02/tado-api-guide-updated-for-2019/
           (tado has no official public docs; this follows the widely-used v2 API)

tado scopes everything under a "home". Each home has "zones"; a heating zone is
the thermostat we surface. Live values come from a zone's ``state`` (the
``sensorDataPoints`` for temperature/humidity, ``setting`` for the target).

UNTESTED: verify against a real device/account — the home-id discovery and zone
state shapes must be confirmed against a live tado account.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from spire import SpireDevice, Trait, VendorAdapter, commands_for

logger = logging.getLogger(__name__)

_BASE_URL = "https://my.tado.com/api/v2"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

_THERMOSTAT_TRAITS = (
    Trait.THERMOSTAT,
    Trait.REPORTS_TEMPERATURE,
    Trait.REPORTS_HUMIDITY,
)


class TadoAdapter(VendorAdapter):
    """tado° adapter. Requires a valid TADO_ACCESS_TOKEN."""

    def __init__(self, access_token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        self._home_id: int | None = None

    async def list_devices(self) -> list[SpireDevice]:
        """Resolve the home, list its zones, and surface heating zones as thermostats."""
        try:
            # UNTESTED: verify against a real device/account.
            home_id = await self._resolve_home_id()
            zones = await self._request("GET", f"/homes/{home_id}/zones")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("tado list_devices failed: %s", exc)
            return []
        devices: list[SpireDevice] = []
        for zone in zones if isinstance(zones, list) else []:
            if zone.get("type") == "HEATING":
                devices.append(_to_spire(home_id, zone, state=None))
        return devices

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /homes/{home}/zones/{zone}/state — live values for one zone."""
        home_id = await self._resolve_home_id()
        # UNTESTED: verify against a real device/account.
        state = await self._request("GET", f"/homes/{home_id}/zones/{device_id}/state")
        zone = {"id": int(device_id), "name": f"Zone {device_id}", "type": "HEATING"}
        return _to_spire(home_id, zone, state=state)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """PUT a manual overlay onto the zone to push a target temperature."""
        home_id = await self._resolve_home_id()
        payload = _translate_command(command)
        # UNTESTED: verify against a real device/account.
        await self._request("PUT", f"/homes/{home_id}/zones/{device_id}/overlay", json=payload)
        return True

    async def _resolve_home_id(self) -> int:
        """GET /me — the account's first home id, cached for the adapter's life."""
        if self._home_id is not None:
            return self._home_id
        me = await self._request("GET", "/me")
        homes = me.get("homes", [])
        if not homes:
            raise ValueError("tado account has no homes")
        self._home_id = int(homes[0]["id"])
        return self._home_id

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """HTTP request with exponential backoff on 429 / network errors."""
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
                    logger.warning("tado rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("tado API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"tado API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command into a tado zone overlay."""
    action = command.get("action", "")
    if action == "set_target_temperature":
        return {
            "setting": {
                "type": "HEATING",
                "power": "ON",
                "temperature": {"celsius": float(command.get("value", 21.0))},
            },
            "termination": {"type": "MANUAL"},
        }
    raise ValueError(f"Unsupported command action for tado: {action!r}")


def _read_state(state: dict[str, Any] | None) -> dict[str, Any]:
    """Pull temperature, humidity, and the target out of a tado zone state."""
    result: dict[str, Any] = {}
    if not state:
        return result
    sensors = state.get("sensorDataPoints", {})
    inside = sensors.get("insideTemperature", {}).get("celsius")
    if inside is not None:
        result["temperature"] = round(float(inside), 1)
    humidity = sensors.get("humidity", {}).get("percentage")
    if humidity is not None:
        result["humidity"] = round(float(humidity), 1)
    target = state.get("setting", {}).get("temperature", {})
    if target and target.get("celsius") is not None:
        result["target_temperature"] = round(float(target["celsius"]), 1)
    return result


def _to_spire(home_id: int, zone: dict[str, Any], *, state: dict[str, Any] | None) -> SpireDevice:
    """Convert a tado heating zone (plus optional live state) into a SpireDevice."""
    zone_id = zone.get("id", "")
    return SpireDevice.from_vendor(
        vendor="tado",
        vendor_id=str(zone_id),
        name=zone.get("name", "tado Thermostat"),
        device_type="thermostat",
        online=True,
        state=_read_state(state),
        supported_commands=commands_for(list(_THERMOSTAT_TRAITS)),
        traits=list(_THERMOSTAT_TRAITS),
    )
