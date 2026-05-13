from __future__ import annotations

import httpx

from config import get_settings

_BASE = "https://openapi.api.govee.com/router/api/v1"

# Govee's free API doesn't return live power state in device listings.
# We track toggled state in memory for the demo session.
_power_state: dict[str, bool] = {}


def _headers() -> dict[str, str]:
    key = get_settings().govee_api_key
    if not key:
        raise RuntimeError("GOVEE_API_KEY is not configured")
    return {"Govee-API-Key": key, "Content-Type": "application/json"}


async def list_devices() -> list[dict[str, object]]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_BASE}/user/devices", headers=_headers())
        r.raise_for_status()
        devices: list[dict[str, object]] = r.json().get("data", [])
        for d in devices:
            device_id = str(d.get("device", d.get("deviceId", "")))
            d["_power"] = _power_state.get(device_id, False)
        return devices


async def set_power(device: str, model: str, *, on: bool) -> dict[str, object]:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_BASE}/device/control",
            headers=_headers(),
            json={
                "requestId": device,
                "payload": {
                    "sku": model,
                    "device": device,
                    "capability": {
                        "type": "devices.capabilities.on_off",
                        "instance": "powerSwitch",
                        "value": 1 if on else 0,
                    },
                },
            },
        )
        r.raise_for_status()
        _power_state[device] = on
        return r.json()  # type: ignore[no-any-return]
