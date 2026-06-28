"""Direct local-network controller for Shelly devices."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = 5.0


class ShellyController:
    def __init__(self, ip: str) -> None:
        self.ip = ip

    async def turn_on(self) -> bool:
        return await self._relay_set(True)

    async def turn_off(self) -> bool:
        return await self._relay_set(False)

    async def get_state(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"http://{self.ip}/rpc/Switch.GetStatus",
                json={"id": 0},
            )
            r.raise_for_status()
            data = r.json()
            aenergy = data.get("aenergy") or {}
            return {
                "on": data.get("output", False),
                "power": float(data.get("apower", 0.0)),
                "voltage": float(data.get("voltage", 0.0)),
                "current": float(data.get("current", 0.0)),
                "energy": float(aenergy.get("total", 0.0)),
            }

    async def get_power(self) -> float:
        state = await self.get_state()
        return float(state["power"])

    async def _relay_set(self, on: bool) -> bool:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.post(
                    f"http://{self.ip}/rpc/Switch.Set",
                    json={"id": 0, "on": on},
                )
                r.raise_for_status()
                return True
        except Exception as exc:
            logger.warning("ShellyController relay command failed for %s: %s", self.ip, exc)
            return False
