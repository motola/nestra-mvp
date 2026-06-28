"""
SwitchBot API (v1.1) client.

Base URL : https://api.switch-bot.com/v1.1
Auth     : token + secret, combined into an HMAC-SHA256 signature sent as the
           ``Authorization``, ``sign``, ``t`` and ``nonce`` headers.
Docs     : https://github.com/OpenWonderLabs/SwitchBotAPI

SwitchBot covers contact/motion/leak sensors, locks, and bots/switches. Each
device has a ``deviceType`` we map to a SPIRE type, and a status payload whose
fields (``moveDetected``, ``openState``, ``battery`` ...) map onto sensor traits.

UNTESTED: verify against a real device/account — built from public docs only.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import logging
import time
import uuid
from typing import Any

import httpx

from spire import SpireDevice, Trait, VendorAdapter, commands_for

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.switch-bot.com/v1.1"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

# SwitchBot deviceType -> (SPIRE device type, explicit traits).
_DEVICE_TYPE_MAP: dict[str, tuple[str, tuple[Trait, ...]]] = {
    "Contact Sensor": (
        "sensor",
        (Trait.REPORTS_CONTACT, Trait.REPORTS_MOTION, Trait.REPORTS_BATTERY),
    ),
    "Motion Sensor": ("sensor", (Trait.REPORTS_MOTION, Trait.REPORTS_BATTERY)),
    "Water Leak Detector": ("sensor", (Trait.REPORTS_LEAK, Trait.REPORTS_BATTERY)),
    "Meter": ("sensor", (Trait.REPORTS_TEMPERATURE, Trait.REPORTS_HUMIDITY, Trait.REPORTS_BATTERY)),
    "MeterPlus": (
        "sensor",
        (Trait.REPORTS_TEMPERATURE, Trait.REPORTS_HUMIDITY, Trait.REPORTS_BATTERY),
    ),
    "Smart Lock": ("lock", (Trait.LOCKABLE, Trait.REPORTS_BATTERY)),
    "Smart Lock Pro": ("lock", (Trait.LOCKABLE, Trait.REPORTS_BATTERY)),
    "Plug Mini (US)": ("plug", (Trait.ON_OFF, Trait.REPORTS_POWER)),
    "Bot": ("plug", (Trait.ON_OFF,)),
}


class SwitchBotAdapter(VendorAdapter):
    """SwitchBot adapter. Requires SWITCHBOT_TOKEN and SWITCHBOT_SECRET."""

    def __init__(self, token: str, secret: str = "") -> None:
        if not secret and ":" in token:
            token, secret = token.split(":", 1)
        self._token = token
        self._secret = secret

    async def list_devices(self) -> list[SpireDevice]:
        """GET /devices — physical device list (infrared remotes are ignored)."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/devices")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("SwitchBot list_devices failed: %s", exc)
            return []
        raw_devices: list[dict[str, Any]] = data.get("body", {}).get("deviceList", [])
        return [_to_spire(d) for d in raw_devices]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /devices/{id}/status — live status merged onto device metadata."""
        # UNTESTED: verify against a real device/account.
        data = await self._request("GET", f"/devices/{device_id}/status")
        return _to_spire(data.get("body", {}))

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """POST /devices/{id}/commands — turnOn / turnOff / lock / unlock."""
        payload = _translate_command(command)
        # UNTESTED: verify against a real device/account.
        await self._request("POST", f"/devices/{device_id}/commands", json=payload)
        return True

    def _auth_headers(self) -> dict[str, str]:
        """Build the SwitchBot v1.1 HMAC signature headers."""
        t = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        message = f"{self._token}{t}{nonce}".encode()
        signature = base64.b64encode(
            hmac.new(self._secret.encode(), message, hashlib.sha256).digest()
        ).decode()
        return {
            "Authorization": self._token,
            "sign": signature,
            "t": t,
            "nonce": nonce,
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """HTTP request with exponential backoff on 429 / network errors."""
        url = f"{_BASE_URL}{path}"
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    r = await client.request(method, url, headers=self._auth_headers(), **kwargs)
                    r.raise_for_status()
                    return r.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("SwitchBot rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("SwitchBot API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"SwitchBot API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _translate_command(command: dict[str, Any]) -> dict[str, Any]:
    """Translate an Alphacon command into a SwitchBot command body."""
    action = command.get("action", "")
    base = {"commandType": "command", "parameter": "default"}
    if action == "turn_on":
        return {**base, "command": "turnOn"}
    if action == "turn_off":
        return {**base, "command": "turnOff"}
    if action == "lock":
        return {**base, "command": "lock"}
    if action == "unlock":
        return {**base, "command": "unlock"}
    raise ValueError(f"Unsupported command action for SwitchBot: {action!r}")


def _read_state(raw: dict[str, Any], traits: tuple[Trait, ...]) -> dict[str, Any]:
    """Pull live sensor/actuator values out of a SwitchBot status payload."""
    state: dict[str, Any] = {}
    if Trait.REPORTS_CONTACT in traits and "openState" in raw:
        state["contact_open"] = raw["openState"] == "open"
    if Trait.REPORTS_MOTION in traits and "moveDetected" in raw:
        state["motion_detected"] = bool(raw["moveDetected"])
    if Trait.REPORTS_LEAK in traits and "status" in raw:
        state["leak_detected"] = raw["status"] == 1
    if Trait.REPORTS_TEMPERATURE in traits and "temperature" in raw:
        state["temperature"] = float(raw["temperature"])
    if Trait.REPORTS_HUMIDITY in traits and "humidity" in raw:
        state["humidity"] = float(raw["humidity"])
    if Trait.REPORTS_BATTERY in traits and "battery" in raw:
        state["battery"] = int(raw["battery"])
    if Trait.LOCKABLE in traits and "lockState" in raw:
        state["locked"] = raw["lockState"] == "locked"
    if Trait.ON_OFF in traits and "power" in raw:
        state["on"] = raw["power"] == "on"
    return state


def _to_spire(raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw SwitchBot device/status object into a SpireDevice."""
    device_type_raw: str = raw.get("deviceType", "")
    mapped = _DEVICE_TYPE_MAP.get(device_type_raw, ("other", ()))
    device_type, traits = mapped
    return SpireDevice.from_vendor(
        vendor="switchbot",
        vendor_id=raw.get("deviceId", ""),
        name=raw.get("deviceName", device_type_raw or "SwitchBot Device"),
        device_type=device_type,
        online=raw.get("online", True) if "online" in raw else True,
        state=_read_state(raw, traits),
        supported_commands=commands_for(list(traits)),
        traits=list(traits),
    )
