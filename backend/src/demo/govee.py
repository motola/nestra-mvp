from __future__ import annotations

import os

import httpx

_BASE = "https://developer-api.govee.com/v1"

# Govee's free API doesn't return live power state in device listings.
# We track toggled state in memory for the demo session.
_power_state: dict[str, bool] = {}


def _headers() -> dict[str, str]:
    key = os.getenv("GOVEE_API_KEY", "")
    return {"Govee-API-Key": key}


async def list_devices() -> list[dict[str, object]]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_BASE}/devices", headers=_headers())
        r.raise_for_status()
        devices: list[dict[str, object]] = r.json()["data"]["devices"]
        for d in devices:
            device_id = str(d["device"])
            d["_power"] = _power_state.get(device_id, False)
        return devices


async def set_power(device: str, model: str, *, on: bool) -> dict[str, object]:
    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{_BASE}/devices/control",
            headers=_headers(),
            json={
                "device": device,
                "model": model,
                "cmd": {"name": "turn", "value": "on" if on else "off"},
            },
        )
        r.raise_for_status()
        _power_state[device] = on
        return r.json()  # type: ignore[no-any-return]
