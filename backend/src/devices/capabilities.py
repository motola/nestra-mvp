"""Device capabilities — the capability-based device model.

A device is the set of capabilities it exposes (its *capabilities*), derived from the
commands it accepts and the readings it reports — never inferred from a product
name or model number. This mirrors how Matter clusters and Google Home capabilities
work, and lets the platform reason about any device uniformly across vendors,
regardless of its nominal "type".
"""

from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    """A single capability a device may support."""

    ON_OFF = "on_off"
    DIMMABLE = "dimmable"
    COLOR = "color"
    COLOR_TEMP = "color_temp"
    LOCKABLE = "lockable"
    REPORTS_POWER = "reports_power"
    REPORTS_TEMPERATURE = "reports_temperature"
    REPORTS_HUMIDITY = "reports_humidity"
    REPORTS_LEAK = "reports_leak"


# Canonical command name → the actuator trait it implies. The single source of
# truth for actuator capabilities; normalisers only emit canonical commands.
_COMMAND_CAPABILITIES: dict[str, Capability] = {
    "turn_on": Capability.ON_OFF,
    "turn_off": Capability.ON_OFF,
    "set_brightness": Capability.DIMMABLE,
    "set_color": Capability.COLOR,
    "set_color_temp": Capability.COLOR_TEMP,
    "lock": Capability.LOCKABLE,
    "unlock": Capability.LOCKABLE,
}


def derive_capabilities(
    supported_commands: list[str],
    *,
    reports_power: bool = False,
    reports_temperature: bool = False,
    reports_humidity: bool = False,
    reports_leak: bool = False,
) -> list[Capability]:
    """Derive a device's capabilities from its canonical commands and reported readings.

    Capability-sourced, de-duplicated, and order-stable. Never infers from a
    model name — actuator capabilities come from the commands the device accepts,
    reporting capabilities from the readings it actually provides.
    """
    capabilities: list[Capability] = []
    for command in supported_commands:
        trait = _COMMAND_CAPABILITIES.get(command)
        if trait is not None and trait not in capabilities:
            capabilities.append(trait)
    reporting = (
        (reports_power, Capability.REPORTS_POWER),
        (reports_temperature, Capability.REPORTS_TEMPERATURE),
        (reports_humidity, Capability.REPORTS_HUMIDITY),
        (reports_leak, Capability.REPORTS_LEAK),
    )
    capabilities.extend(trait for present, trait in reporting if present)
    return capabilities
