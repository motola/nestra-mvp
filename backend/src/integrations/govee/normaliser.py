"""
Govee → AlphaconDevice normaliser.

After this module, no Govee field names (powerState, colorTem, supportCmds, etc.)
should appear anywhere else in the codebase. This is the translation boundary.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from devices.models import AlphaconDevice
from devices.traits import derive_traits

# Maps Govee model prefixes to Alphacon device types.
# Govee model naming: first 4 chars identify the product line.
_MODEL_TYPE_MAP: dict[str, str] = {
    # Light strips
    "H617": "light",
    "H618": "light",
    "H619": "light",
    "H615": "light",
    "H614": "light",
    # Bulbs / lamps
    "H600": "light",
    "H601": "light",
    "H604": "light",
    "H606": "light",
    "H607": "light",
    "H608": "light",
    # Smart plugs
    "H500": "plug",
    "H501": "plug",
    # Thermo-hygrometers / sensors
    "H518": "sensor",
    "H507": "sensor",
    "H517": "sensor",
}


def _infer_type(model: str) -> str:
    """Infer device type from Govee model number prefix."""
    prefix = model[:4].upper()
    return _MODEL_TYPE_MAP.get(prefix, "light")


def _flatten_properties(props: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Govee state returns properties as a list of single-key dicts.
    Flatten them into one dict for easy access.
    Example: [{"online": true}, {"powerState": "on"}] → {"online": true, "powerState": "on"}
    """
    result: dict[str, Any] = {}
    for item in props:
        result.update(item)
    return result


def normalise_device(raw: dict[str, Any]) -> AlphaconDevice:
    """
    Convert a raw Govee device object (from GET /devices) into AlphaconDevice.
    The device list response does not include live state — only metadata.
    """
    model: str = raw.get("model", "")
    mac: str = raw.get("device", "")
    # supportCmds is Govee's capability declaration — the source of truth for
    # what this device can do. Map it to canonical commands, then to traits.
    commands = _map_commands(raw.get("supportCmds", []))

    return AlphaconDevice(
        vendor_id=f"{mac}::{model}",
        vendor="govee",
        name=raw.get("deviceName", f"Govee {model}"),
        type=_infer_type(model),
        online=False,
        controllable=bool(raw.get("controllable", False)),
        state={},
        last_seen=datetime.now(UTC),
        supported_commands=commands,
        traits=derive_traits(commands),
    )


def normalise_state(raw: dict[str, Any]) -> AlphaconDevice:
    """
    Convert a raw Govee state object (from GET /devices/state) into AlphaconDevice.
    The state response includes live values for online, power, brightness, colour.
    """
    model: str = raw.get("model", "")
    mac: str = raw.get("device", "")
    props = _flatten_properties(raw.get("properties", []))

    online: bool = bool(props.get("online", False))
    power_on: bool = props.get("powerState", "off") == "on"

    state: dict[str, Any] = {"on": power_on}

    brightness = props.get("brightness")
    if brightness is not None:
        state["brightness"] = int(brightness)

    color = props.get("color")
    if color:
        state["color"] = {
            "r": int(color.get("r", 255)),
            "g": int(color.get("g", 255)),
            "b": int(color.get("b", 255)),
        }

    color_temp = props.get("colorTemInKelvin")
    if color_temp is not None:
        state["color_temp_kelvin"] = int(color_temp)

    return AlphaconDevice(
        vendor_id=f"{mac}::{model}",
        vendor="govee",
        name=raw.get("deviceName", f"Govee {model}"),
        type=_infer_type(model),
        online=online,
        # Controllability is a static capability — derive it from evidence in the
        # live state (a reported power state) rather than asserting it per-endpoint.
        controllable="powerState" in props,
        state=state,
        last_seen=datetime.now(UTC),
    )


def _map_commands(govee_cmds: list[str]) -> list[str]:
    """Translate Govee supportCmds into Alphacon command names."""
    mapping = {
        "turn": ["turn_on", "turn_off"],
        "brightness": ["set_brightness"],
        "color": ["set_color"],
        "colorTem": ["set_color_temp"],
    }
    result: list[str] = []
    for cmd in govee_cmds:
        result.extend(mapping.get(cmd, []))
    return result
