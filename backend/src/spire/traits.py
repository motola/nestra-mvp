"""Device traits — the capability-based device model.

A device is the set of traits it exposes, derived from the commands it accepts
and the readings it reports — never inferred from a product name. This mirrors
Matter clusters and Google Home traits, letting the platform reason about any
device uniformly across vendors.

Each trait has a formal spec in ``TRAIT_CATALOG``: which key it occupies in a
device's ``state``, the unit/type of that value, and (for actuators) the
canonical commands it accepts. That catalog is what makes SPIRE *interoperable*
rather than merely consistent — two implementations agree on exactly where
brightness lives and how to set it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel


class Trait(StrEnum):
    """A single capability a device may support."""

    # Actuators — things a device can be told to do.
    ON_OFF = "on_off"
    DIMMABLE = "dimmable"
    COLOR = "color"
    COLOR_TEMP = "color_temp"
    LOCKABLE = "lockable"
    FAN_SPEED = "fan_speed"
    THERMOSTAT = "thermostat"
    OPEN_CLOSE = "open_close"

    # Sensors — things a device reports.
    REPORTS_POWER = "reports_power"
    REPORTS_TEMPERATURE = "reports_temperature"
    REPORTS_HUMIDITY = "reports_humidity"
    REPORTS_LEAK = "reports_leak"
    REPORTS_BATTERY = "reports_battery"
    REPORTS_MOTION = "reports_motion"
    REPORTS_CONTACT = "reports_contact"
    REPORTS_SMOKE = "reports_smoke"
    REPORTS_CO = "reports_co"
    REPORTS_ILLUMINANCE = "reports_illuminance"
    REPORTS_OCCUPANCY = "reports_occupancy"


@dataclass(frozen=True)
class TraitSpec:
    """The formal contract for one trait — its state shape and (if any) commands."""

    kind: Literal["actuator", "sensor"]
    state_key: str  # the key under SpireDevice.state this trait reads/writes
    value_type: str  # "bool" | "percent" | "celsius" | "kelvin" | "rgb" | "watts" | "lux"
    commands: tuple[str, ...] = field(default_factory=tuple)  # canonical commands (actuators)


# The single source of truth: every trait, the state it carries, and its commands.
TRAIT_CATALOG: dict[Trait, TraitSpec] = {
    Trait.ON_OFF: TraitSpec("actuator", "on", "bool", ("turn_on", "turn_off")),
    Trait.DIMMABLE: TraitSpec("actuator", "brightness", "percent", ("set_brightness",)),
    Trait.COLOR: TraitSpec("actuator", "color", "rgb", ("set_color",)),
    Trait.COLOR_TEMP: TraitSpec("actuator", "color_temp_kelvin", "kelvin", ("set_color_temp",)),
    Trait.LOCKABLE: TraitSpec("actuator", "locked", "bool", ("lock", "unlock")),
    Trait.FAN_SPEED: TraitSpec("actuator", "fan_speed", "percent", ("set_fan_speed",)),
    Trait.THERMOSTAT: TraitSpec(
        "actuator", "target_temperature", "celsius", ("set_target_temperature",)
    ),
    Trait.OPEN_CLOSE: TraitSpec(
        "actuator", "position", "percent", ("set_position", "open", "close")
    ),
    Trait.REPORTS_POWER: TraitSpec("sensor", "power", "watts"),
    Trait.REPORTS_TEMPERATURE: TraitSpec("sensor", "temperature", "celsius"),
    Trait.REPORTS_HUMIDITY: TraitSpec("sensor", "humidity", "percent"),
    Trait.REPORTS_LEAK: TraitSpec("sensor", "leak_detected", "bool"),
    Trait.REPORTS_BATTERY: TraitSpec("sensor", "battery", "percent"),
    Trait.REPORTS_MOTION: TraitSpec("sensor", "motion_detected", "bool"),
    Trait.REPORTS_CONTACT: TraitSpec("sensor", "contact_open", "bool"),
    Trait.REPORTS_SMOKE: TraitSpec("sensor", "smoke_detected", "bool"),
    Trait.REPORTS_CO: TraitSpec("sensor", "co_detected", "bool"),
    Trait.REPORTS_ILLUMINANCE: TraitSpec("sensor", "illuminance", "lux"),
    Trait.REPORTS_OCCUPANCY: TraitSpec("sensor", "occupied", "bool"),
}

# Derived from the catalog so there is one source of truth: command → trait.
_COMMAND_TRAITS: dict[str, Trait] = {
    command: trait for trait, spec in TRAIT_CATALOG.items() for command in spec.commands
}


class Command(BaseModel):
    """A canonical command sent to a device — the value follows the trait's spec."""

    action: str  # e.g. "set_brightness"; must be a command in TRAIT_CATALOG
    value: Any = None  # e.g. 80 for set_brightness (a percent)


def commands_for(traits: list[Trait]) -> list[str]:
    """Every canonical command a device with these traits accepts."""
    result: list[str] = []
    for trait in traits:
        for command in TRAIT_CATALOG[trait].commands:
            if command not in result:
                result.append(command)
    return result


class TraitState(BaseModel):
    """The current value of one trait, pulled from a device's state and typed via the catalog.

    Turns a loose ``state`` dict into a self-describing, per-trait view: which trait,
    its value, and the unit/type that value is in. This is what lets a consumer read
    "brightness is 80 percent" without guessing where it lives.
    """

    trait: Trait
    value: Any
    unit: str  # the catalog value_type, e.g. "percent", "celsius", "bool"


def read_trait_states(traits: list[Trait], state: dict[str, Any]) -> list[TraitState]:
    """Typed current state for each trait that has a value present in ``state``."""
    result: list[TraitState] = []
    for trait in traits:
        spec = TRAIT_CATALOG[trait]
        if spec.state_key in state:
            result.append(
                TraitState(trait=trait, value=state[spec.state_key], unit=spec.value_type)
            )
    return result


def derive_traits(
    supported_commands: list[str],
    *,
    reports_power: bool = False,
    reports_temperature: bool = False,
    reports_humidity: bool = False,
    reports_leak: bool = False,
) -> list[Trait]:
    """Derive a device's traits from its canonical commands and reported readings.

    Capability-sourced, de-duplicated, order-stable. Never infers from a model
    name — actuator traits come from the commands the device accepts, the common
    reporting traits from the readings it provides. (Less common sensor traits are
    set explicitly by an adapter.)
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
