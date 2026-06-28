"""Vendor registry — the single source of truth for supported integrations.

Adding a vendor is a single entry here. The device service, the integrations
API, and any vendor lookups all derive from this registry, so there are no
hand-maintained lists scattered across the codebase to drift out of sync.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from config import Settings
from integrations.aqara.adapter import AqaraAdapter
from integrations.august.adapter import AugustAdapter
from integrations.ecobee.adapter import EcobeeAdapter
from integrations.ewelink.adapter import EWeLinkAdapter
from integrations.govee.adapter import GoveeAdapter
from integrations.hue.adapter import HueAdapter
from integrations.kasa.adapter import KasaAdapter
from integrations.lifx.adapter import LIFXAdapter
from integrations.smartthings.adapter import SmartThingsAdapter
from integrations.switchbot.adapter import SwitchBotAdapter
from integrations.tado.adapter import TadoAdapter
from integrations.tuya.adapter import TuyaAdapter
from spire import VendorAdapter


@dataclass(frozen=True)
class VendorSpec:
    """Everything the platform needs to know about one integration."""

    name: str
    display_name: str
    description: str
    # Settings attribute holding the credential; None for local/protocol vendors.
    settings_key: str | None = None
    # Builds the vendor's cloud-poll adapter from its credential, if it has one.
    adapter: Callable[[str], VendorAdapter] | None = None

    def is_connected(self, settings: Settings) -> bool:
        """Local/protocol vendors are always available; cloud vendors need a credential."""
        if self.settings_key is None:
            return True
        return bool(getattr(settings, self.settings_key, ""))

    def build_adapter(self, settings: Settings) -> VendorAdapter | None:
        """Construct this vendor's adapter, or None if it has no credential configured."""
        if self.adapter is None or self.settings_key is None:
            return None
        credential = getattr(settings, self.settings_key, "")
        return self.adapter(credential) if credential else None


VENDOR_REGISTRY: tuple[VendorSpec, ...] = (
    VendorSpec("govee", "Govee", "Smart lights and plugs", "govee_api_key", GoveeAdapter),
    VendorSpec("shelly", "Shelly", "Smart plugs and switches", "shelly_auth_key"),
    VendorSpec("lifx", "LIFX", "Wi-Fi smart bulbs", "lifx_api_token", LIFXAdapter),
    VendorSpec("matter", "Matter", "Universal smart home standard"),
    VendorSpec("hue", "Philips Hue", "Smart lighting", "hue_api_key", HueAdapter),
    VendorSpec(
        "smartthings",
        "SmartThings",
        "Samsung smart home hub",
        "smartthings_token",
        SmartThingsAdapter,
    ),
    VendorSpec("tuya", "Tuya", "Smart plugs, lights and sensors", "tuya_access_id", TuyaAdapter),
    VendorSpec(
        "switchbot",
        "SwitchBot",
        "Sensors, locks and switches",
        "switchbot_token",
        SwitchBotAdapter,
    ),
    VendorSpec("ecobee", "ecobee", "Smart thermostats", "ecobee_access_token", EcobeeAdapter),
    VendorSpec("tado", "tado°", "Smart thermostats", "tado_access_token", TadoAdapter),
    VendorSpec("kasa", "TP-Link Kasa", "Smart plugs and switches", "kasa_token", KasaAdapter),
    VendorSpec("august", "August", "Smart locks", "august_access_token", AugustAdapter),
    VendorSpec("aqara", "Aqara", "Smart sensors", "aqara_access_token", AqaraAdapter),
    VendorSpec(
        "ewelink",
        "eWeLink",
        "Sonoff switches and plugs",
        "ewelink_access_token",
        EWeLinkAdapter,
    ),
)

VENDOR_NAMES: tuple[str, ...] = tuple(v.name for v in VENDOR_REGISTRY)
