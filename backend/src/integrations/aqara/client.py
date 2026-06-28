"""
Aqara Cloud (Open API) client.

Base URL : https://open-cn.aqara.com   (region-specific; CN shown)
Auth     : signed requests using AppId + KeyId + AppKey (HMAC-style ``Sign``
           header) plus an OAuth access token for account-scoped data.
Docs     : https://opendoc.aqara.com/en/

Aqara is a sensor-heavy ecosystem (motion, contact/door, water leak, temperature
and humidity). Devices are listed via the ``query.device.info`` intent; live
values come from ``query.resource.value`` against a device's resource ids. We map
the Aqara ``model`` family onto SPIRE sensor traits.

UNTESTED: verify against a real device/account — the resource-id catalog per
model and the exact sign algorithm must be confirmed against a live Aqara app.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from typing import Any

import httpx

from spire import SpireDevice, Trait, VendorAdapter, commands_for

logger = logging.getLogger(__name__)

_BASE_URL = "https://open-cn.aqara.com"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

# Aqara model-name fragments -> explicit SPIRE sensor traits.
_MODEL_TRAIT_MAP: tuple[tuple[str, tuple[Trait, ...]], ...] = (
    ("motion", (Trait.REPORTS_MOTION, Trait.REPORTS_BATTERY)),
    ("magnet", (Trait.REPORTS_CONTACT, Trait.REPORTS_BATTERY)),
    ("contact", (Trait.REPORTS_CONTACT, Trait.REPORTS_BATTERY)),
    ("flood", (Trait.REPORTS_LEAK, Trait.REPORTS_BATTERY)),
    ("leak", (Trait.REPORTS_LEAK, Trait.REPORTS_BATTERY)),
    ("weather", (Trait.REPORTS_TEMPERATURE, Trait.REPORTS_HUMIDITY, Trait.REPORTS_BATTERY)),
    ("th", (Trait.REPORTS_TEMPERATURE, Trait.REPORTS_HUMIDITY, Trait.REPORTS_BATTERY)),
)


class AqaraAdapter(VendorAdapter):
    """Aqara cloud adapter. Requires an AQARA_ACCESS_TOKEN (packed credential)."""

    def __init__(
        self, access_token: str, app_id: str = "", app_key: str = "", key_id: str = ""
    ) -> None:
        # Credentials may be packed as "token:appId:appKey:keyId" so the registry
        # can pass a single settings value; unpack when the extra parts are absent.
        if not app_id and ":" in access_token:
            parts = access_token.split(":")
            access_token = parts[0]
            app_id = parts[1] if len(parts) > 1 else ""
            app_key = parts[2] if len(parts) > 2 else ""
            key_id = parts[3] if len(parts) > 3 else ""
        self._access_token = access_token
        self._app_id = app_id
        self._app_key = app_key
        self._key_id = key_id

    async def list_devices(self) -> list[SpireDevice]:
        """POST the query.device.info intent — every device on the account."""
        body = {"intent": "query.device.info", "data": {"pageSize": 100}}
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request(body)
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("Aqara list_devices failed: %s", exc)
            return []
        raw_devices: list[dict[str, Any]] = data.get("result", {}).get("data", [])
        return [_to_spire(d, values={}) for d in raw_devices]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """POST query.resource.value for a device, then map values onto state."""
        body = {
            "intent": "query.resource.value",
            "data": {"resources": [{"subjectId": device_id}]},
        }
        # UNTESTED: verify against a real device/account.
        data = await self._request(body)
        results: list[dict[str, Any]] = data.get("result", [])
        values = {item.get("resourceId"): item.get("value") for item in results}
        return _to_spire({"did": device_id, "model": ""}, values=values)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """Aqara devices here are sensors; no actuator commands are supported."""
        raise ValueError(f"Aqara sensors do not accept commands: {command.get('action')!r}")

    def _sign_headers(self, nonce: str, t: str) -> dict[str, str]:
        """Build the Aqara ``Sign`` header from the app credentials."""
        raw = (
            f"accesstoken={self._access_token}&appid={self._app_id}"
            f"&keyid={self._key_id}&nonce={nonce}&time={t}{self._app_key}"
        ).lower()
        return {
            "Appid": self._app_id,
            "Keyid": self._key_id,
            "Nonce": nonce,
            "Time": t,
            "Accesstoken": self._access_token,
            "Sign": hashlib.md5(raw.encode()).hexdigest(),  # noqa: S324 (vendor-mandated MD5)
            "Content-Type": "application/json",
        }

    async def _request(self, body: dict[str, Any]) -> dict[str, Any]:
        """POST a signed intent to the Aqara gateway with backoff on errors."""
        url = f"{_BASE_URL}/v3.0/open/api"
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                nonce = uuid.uuid4().hex
                t = str(int(time.time() * 1000))
                headers = self._sign_headers(nonce, t)
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    r = await client.post(url, headers=headers, json=body)
                    r.raise_for_status()
                    return r.json()  # type: ignore[no-any-return]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning("Aqara rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("Aqara API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"Aqara API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _traits_for(model: str) -> tuple[Trait, ...]:
    """Pick sensor traits from a recognised fragment of the Aqara model name."""
    lowered = model.lower()
    for fragment, traits in _MODEL_TRAIT_MAP:
        if fragment in lowered:
            return traits
    return (Trait.REPORTS_BATTERY,)


def _to_spire(raw: dict[str, Any], *, values: dict[Any, Any]) -> SpireDevice:
    """Convert a raw Aqara device object into a SpireDevice."""
    model: str = raw.get("model", "")
    traits = _traits_for(model)

    state: dict[str, Any] = {}
    # Aqara resource values are strings keyed by resourceId; only fold in the ones
    # we can interpret generically (model-specific resource ids vary per product).
    for key, value in values.items():
        if key in ("3.1.85", "13.1.85") and Trait.REPORTS_MOTION in traits:
            state["motion_detected"] = str(value) == "1"
        elif key == "3.1.85" and Trait.REPORTS_CONTACT in traits:
            state["contact_open"] = str(value) == "1"

    return SpireDevice.from_vendor(
        vendor="aqara",
        vendor_id=raw.get("did", ""),
        name=raw.get("deviceName") or model or "Aqara Sensor",
        device_type="sensor",
        online=raw.get("state", 1) == 1 if "state" in raw else True,
        state=state,
        supported_commands=commands_for(list(traits)),
        traits=list(traits),
    )
