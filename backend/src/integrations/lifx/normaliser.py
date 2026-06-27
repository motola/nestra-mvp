"""
LIFX Cloud → SpireDevice normaliser.

After this module, no LIFX field names (connected, color, kelvin, etc.)
should appear anywhere else in the codebase.
"""

from __future__ import annotations

from typing import Any

from spire import SpireDevice


def normalise_device(raw: dict[str, Any]) -> SpireDevice:
    """Convert a raw LIFX light object into SpireDevice."""
    product: dict[str, Any] = raw.get("product", {})
    color: dict[str, Any] = raw.get("color", {})
    power: str = raw.get("power", "off")

    state: dict[str, Any] = {
        "on": power == "on",
        "brightness": round(float(raw.get("brightness", 1.0)) * 100),
    }

    if color:
        state["color_temp_kelvin"] = int(color.get("kelvin", 3500))
        hue = color.get("hue", 0)
        saturation = color.get("saturation", 0)
        if saturation > 0.05:
            state["hue"] = hue
            state["saturation"] = saturation

    commands = ["turn_on", "turn_off", "set_brightness"]
    if product.get("capabilities", {}).get("has_color", False):
        commands.append("set_color")

    return SpireDevice.from_vendor(
        vendor="lifx",
        vendor_id=raw.get("id", ""),
        name=raw.get("label", "LIFX Light"),
        device_type="light",
        online=bool(raw.get("connected", False)),
        state=state,
        supported_commands=commands,
    )
