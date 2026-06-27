"""Device traits — the capability-based device model.

A device is the set of capabilities it exposes (its *traits*), derived from the
commands it accepts and the readings it reports — never inferred from a product
name or model number. This mirrors how Matter clusters and Google Home traits
work, and lets the platform reason about any device uniformly across vendors,
regardless of its nominal "type".
"""

from __future__ import annotations

from enum import StrEnum


class Trait(StrEnum):
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
_COMMAND_TRAITS: dict[str, Trait] = {
    "turn_on": Trait.ON_OFF,
    "turn_off": Trait.ON_OFF,
    "set_brightness": Trait.DIMMABLE,
    "set_color": Trait.COLOR,
    "set_color_temp": Trait.COLOR_TEMP,
    "lock": Trait.LOCKABLE,
    "unlock": Trait.LOCKABLE,
}


def derive_traits(
    supported_commands: list[str],
    *,
    reports_power: bool = False,
    reports_temperature: bool = False,
    reports_humidity: bool = False,
    reports_leak: bool = False,
) -> list[Trait]:
    """Derive a device's traits from its canonical commands and reported readings.

    Capability-sourced, de-duplicated, and order-stable. Never infers from a
    model name — actuator traits come from the commands the device accepts,
    reporting traits from the readings it actually provides.
    """
    traits: list[Trait] = []
    for command in supported_commands:
        trait = _COMMAND_TRAITS.get(command)
        if trait is not None and trait not in traits:
            traits.append(trait)
    reporting = (
        (reports_power, Trait.REPORTS_POWER),
        (reports_temperature, Trait.REPORTS_TEMPERATURE),
        (reports_humidity, Trait.REPORTS_HUMIDITY),
        (reports_leak, Trait.REPORTS_LEAK),
    )
    traits.extend(trait for present, trait in reporting if present)
    return traits
