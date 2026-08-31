"""Provider definitions - supported platforms/protocols/vendors."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    """Definition of a supported provider/platform."""

    id: str  # "bluetooth", "shelly", "lifx", "govee", "meross"
    name: str  # "Bluetooth", "Shelly", "LIFX", "Govee", "Meross"
    slug: str  # "bluetooth", "shelly", etc.
    icon: str = ""


# Supported providers
BLUETOOTH = Provider(
    id="bluetooth",
    name="Bluetooth",
    slug="bluetooth",
    icon="📱",
)

SHELLY = Provider(
    id="shelly",
    name="Shelly",
    slug="shelly",
    icon="⚡",
)

LIFX = Provider(
    id="lifx",
    name="LIFX",
    slug="lifx",
    icon="💡",
)

GOVEE = Provider(
    id="govee",
    name="Govee",
    slug="govee",
    icon="🎨",
)

MEROSS = Provider(
    id="meross",
    name="Meross",
    slug="meross",
    icon="🏠",
)

PROVIDERS = {
    "bluetooth": BLUETOOTH,
    "shelly": SHELLY,
    "lifx": LIFX,
    "govee": GOVEE,
    "meross": MEROSS,
}


def get_provider(provider_id: str) -> Provider | None:
    """Get provider by ID."""
    return PROVIDERS.get(provider_id)
