"""Normalise Shelly local-RPC state into the vendor-agnostic SpireDevice."""

from __future__ import annotations

from typing import Any

from spire import SpireDevice

_SUPPORTED_COMMANDS = ["turn_on", "turn_off"]


def to_spire_device(
    *,
    device_id: str,
    vendor_id: str,
    name: str,
    state: dict[str, Any],
) -> SpireDevice:
    """Build a SpireDevice from a ShellyLocalController.get_state() result."""
    power = float(state["power"]) if state.get("power") is not None else None
    return SpireDevice.from_vendor(
        vendor="shelly",
        vendor_id=vendor_id,
        name=name,
        device_type="plug",
        online=True,
        state={"on": bool(state.get("on", False)), "power": float(state.get("power", 0.0))},
        power_draw=power,
        supported_commands=list(_SUPPORTED_COMMANDS),
    )


def offline_device(*, device_id: str, vendor_id: str, name: str) -> SpireDevice:
    """Represent an unreachable Shelly device as offline."""
    return SpireDevice.from_vendor(
        vendor="shelly",
        vendor_id=vendor_id,
        name=name,
        device_type="plug",
        online=False,
        supported_commands=list(_SUPPORTED_COMMANDS),
    )
