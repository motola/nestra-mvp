from __future__ import annotations

import httpx

from config import get_settings

_BASE = "https://api.lifx.com/v1"


def _headers() -> dict[str, str]:
    token = get_settings().lifx_api_token
    if not token:
        raise RuntimeError("LIFX_API_TOKEN is not configured")
    return {"Authorization": f"Bearer {token}"}


async def list_lights() -> list[dict[str, object]]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_BASE}/lights/all", headers=_headers())
        r.raise_for_status()
        return r.json()  # type: ignore[no-any-return]


async def set_power(selector: str, power: str) -> dict[str, object]:
    """power: 'on' or 'off'."""
    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{_BASE}/lights/{selector}/state",
            headers=_headers(),
            json={"power": power},
        )
        r.raise_for_status()
        return r.json()  # type: ignore[no-any-return]


async def set_brightness(selector: str, brightness: float) -> dict[str, object]:
    """brightness: 0.0–1.0."""
    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{_BASE}/lights/{selector}/state",
            headers=_headers(),
            json={"brightness": brightness},
        )
        r.raise_for_status()
        return r.json()  # type: ignore[no-any-return]
