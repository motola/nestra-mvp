"""Normalise Shelly local-RPC state into the vendor-agnostic AlphaconDevice."""

from __future__ import annotations

from typing import Any

from devices.models import AlphaconDevice
from devices.traits import derive_traits

_SUPPORTED_COMMANDS = ["turn_on", "turn_off"]


def to_alphacon_device(
    *,
    device_id: str,
    vendor_id: str,
    name: str,
    state: dict[str, Any],
) -> AlphaconDevice:
    """Build an AlphaconDevice from a ShellyLocalController.get_state() result."""
    return AlphaconDevice(
        id=device_id,
        vendor_id=vendor_id,
        vendor="shelly",
        name=name,
        type="plug",
        online=True,
        controllable=True,
        state={"on": bool(state.get("on", False)), "power": float(state.get("power", 0.0))},
        power_draw=float(state["power"]) if state.get("power") is not None else None,
        supported_commands=list(_SUPPORTED_COMMANDS),
        traits=derive_traits(_SUPPORTED_COMMANDS, reports_power=state.get("power") is not None),
    )


def offline_device(*, device_id: str, vendor_id: str, name: str) -> AlphaconDevice:
    """Represent an unreachable Shelly device as offline."""
    return AlphaconDevice(
        id=device_id,
        vendor_id=vendor_id,
        vendor="shelly",
        name=name,
        type="plug",
        online=False,
        controllable=False,
        supported_commands=list(_SUPPORTED_COMMANDS),
        traits=derive_traits(_SUPPORTED_COMMANDS),
    )
