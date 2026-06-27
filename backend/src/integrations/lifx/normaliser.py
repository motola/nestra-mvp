"""
LIFX Cloud → AlphaconDevice normaliser.

After this module, no LIFX field names (connected, color, kelvin, etc.)
should appear anywhere else in the codebase.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from devices.models import AlphaconDevice


def normalise_device(raw: dict[str, Any]) -> AlphaconDevice:
    """Convert a raw LIFX light object into AlphaconDevice."""
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

    return AlphaconDevice(
        id=str(uuid.uuid4()),
        vendor_id=raw.get("id", ""),
        vendor="lifx",
        name=raw.get("label", "LIFX Light"),
        type="light",
        online=bool(raw.get("connected", False)),
        controllable=True,
        state=state,
        last_seen=datetime.now(UTC),
        supported_commands=commands,
    )
