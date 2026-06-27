"""Normalise Shelly local-RPC state into the vendor-agnostic SpireDevice."""

from __future__ import annotations

from typing import Any

from devices.models import SpireDevice
from devices.traits import derive_traits

_SUPPORTED_COMMANDS = ["turn_on", "turn_off"]


def to_spire_device(
    *,
    device_id: str,
    vendor_id: str,
    name: str,
    state: dict[str, Any],
) -> SpireDevice:
    """Build a SpireDevice from a ShellyLocalController.get_state() result."""
    return SpireDevice(
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


def offline_device(*, device_id: str, vendor_id: str, name: str) -> SpireDevice:
    """Represent an unreachable Shelly device as offline."""
    return SpireDevice(
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
