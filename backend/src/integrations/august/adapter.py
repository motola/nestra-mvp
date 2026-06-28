"""
August / Yale Access API client.

Base URL : https://api-production.august.com
Auth     : x-august-access-token header, plus a configurable x-august-api-key.
Docs     : unofficial (August has no public API); this follows the widely-used
           production endpoints documented by the yalexs / py-august community.

August surfaces smart locks. ``GET /users/locks/mine`` lists the account's locks;
a lock's live status (locked/unlocked, door open/closed, battery) is read per
lock and the lock/unlock operations are simple PUT calls.

UNTESTED: verify against a real device/account — the access-token lifecycle
(phone/email validation) must be handled before these calls succeed.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from config import get_settings
from spire import SpireDevice, Trait, VendorAdapter, commands_for

logger = logging.getLogger(__name__)

_BASE_URL = "https://api-production.august.com"
_TIMEOUT = 10.0
_MAX_RETRIES = 3

_LOCK_TRAITS = (Trait.LOCKABLE, Trait.REPORTS_BATTERY)

# August lockStatus / status string -> locked boolean.
_LOCK_STATE_MAP: dict[str, bool] = {
    "locked": True,
    "kAugLockState_Locked": True,
    "unlocked": False,
    "kAugLockState_Unlocked": False,
}


class AugustAdapter(VendorAdapter):
    """August/Yale lock adapter. Requires a valid AUGUST_ACCESS_TOKEN."""

    def __init__(self, access_token: str) -> None:
        self._headers = {
            "x-august-access-token": access_token,
            "x-august-api-key": get_settings().august_api_key,
            "Content-Type": "application/json",
        }

    async def list_devices(self) -> list[SpireDevice]:
        """GET /users/locks/mine — a map of lockId -> lock metadata."""
        try:
            # UNTESTED: verify against a real device/account.
            data = await self._request("GET", "/users/locks/mine")
        except (httpx.HTTPError, RuntimeError, ValueError) as exc:
            logger.error("August list_devices failed: %s", exc)
            return []
        return [_to_spire(lock_id, raw) for lock_id, raw in data.items()]

    async def get_device_state(self, device_id: str) -> SpireDevice:
        """GET /locks/{id} — full status (lock state, door state, battery)."""
        # UNTESTED: verify against a real device/account.
        data = await self._request("GET", f"/locks/{device_id}")
        return _to_spire(device_id, data)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """PUT /remoteoperate/{id}/lock|unlock — drive the lock."""
        action = command.get("action", "")
        if action == "lock":
            verb = "lock"
        elif action == "unlock":
            verb = "unlock"
        else:
            raise ValueError(f"Unsupported command action for August: {action!r}")
        # UNTESTED: verify against a real device/account.
        await self._request("PUT", f"/remoteoperate/{device_id}/{verb}")
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
                    logger.warning("August rate limit hit, retrying in %ss", wait)
                    await asyncio.sleep(wait)
                    last_exc = exc
                else:
                    logger.error("August API error %s", exc.response.status_code)
                    raise
            except httpx.HTTPError as exc:
                await asyncio.sleep(2**attempt)
                last_exc = exc

        raise RuntimeError(f"August API unreachable after {_MAX_RETRIES} attempts") from last_exc


def _to_spire(lock_id: str, raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw August lock object into a SpireDevice."""
    state: dict[str, Any] = {}
    status = raw.get("LockStatus", {})
    lock_state = status.get("status") if isinstance(status, dict) else raw.get("status")
    if lock_state in _LOCK_STATE_MAP:
        state["locked"] = _LOCK_STATE_MAP[lock_state]

    battery = raw.get("battery")
    if battery is not None:
        # August reports battery as a 0..1 fraction; express as a percent.
        state["battery"] = round(float(battery) * 100)

    online = True
    if isinstance(status, dict) and "doorState" in status:
        online = status.get("doorState") != "kAugDoorState_Init"

    return SpireDevice.from_vendor(
        vendor="august",
        vendor_id=lock_id,
        name=raw.get("LockName") or raw.get("name", "August Lock"),
        device_type="lock",
        online=online,
        state=state,
        supported_commands=commands_for(list(_LOCK_TRAITS)),
        traits=list(_LOCK_TRAITS),
    )
