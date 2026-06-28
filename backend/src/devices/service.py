"""
Device service — polls all configured vendor adapters and aggregates results.

This is the single entry point for device data across the platform.
It knows about vendor adapters; the API layer does not.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from spire import SpireDevice

logger = logging.getLogger(__name__)


def _spire_from_flat(d: dict[str, Any]) -> SpireDevice:
    """Build a SpireDevice from a flat demo-device dict (demo.data.demo_device_as_spire)."""
    device = SpireDevice.from_vendor(
        vendor=d["vendor"],
        vendor_id=d.get("vendor_id", d["id"]),
        name=d["name"],
        device_type=d.get("type", "plug"),
        online=d.get("online", True),
        state=d.get("state", {}),
        power_draw=d.get("power_draw"),
        temperature=d.get("temperature"),
        humidity=d.get("humidity"),
        leak_detected=d.get("leak_detected"),
        supported_commands=d.get("supported_commands"),
    )
    device.placement.property_id = d.get("property_id")
    device.placement.room_id = d.get("room_id")
    return device


async def list_all_devices(settings: Settings, session: AsyncSession) -> list[SpireDevice]:
    """
    Return all devices: demo data (if demo mode), cloud vendor APIs,
    and saved registry devices (Shelly, Matter from the database).
    """
    devices: list[SpireDevice] = []

    if settings.demo_mode:
        from demo.data import DEMO_DEVICES, demo_device_as_spire

        devices.extend([_spire_from_flat(demo_device_as_spire(d)) for d in DEMO_DEVICES])

    # Poll every cloud vendor that has a configured credential — driven entirely
    # by the vendor registry, so adding a vendor needs no change here.
    from integrations.registry import VENDOR_REGISTRY

    for spec in VENDOR_REGISTRY:
        adapter = spec.build_adapter(settings)
        if adapter is None:
            continue
        try:
            vendor_devices = await adapter.list_devices()
            devices.extend(vendor_devices)
            logger.info("%s: fetched %d devices", spec.display_name, len(vendor_devices))
        except Exception as exc:
            logger.error("%s poll failed: %s", spec.display_name, exc)

    try:
        from devices.registry import list_devices as _list_registry

        rows = await _list_registry(session)
        devices.extend([_row_to_spire(row) for row in rows])
        logger.info("Registry: fetched %d saved devices", len(rows))
    except Exception as exc:
        logger.error("Registry device list failed: %s", exc)

    return devices


async def get_device(
    device_id: str, settings: Settings, session: AsyncSession
) -> SpireDevice | None:
    """Return current state for a single device. Checks vendor APIs first, falls back to DB."""
    if settings.demo_mode:
        from demo.data import demo_device_as_spire, get_demo_device, is_demo_device

        if is_demo_device(device_id):
            d = get_demo_device(device_id)
            return _spire_from_flat(demo_device_as_spire(d)) if d else None

    all_devices = await list_all_devices(settings, session)
    for device in all_devices:
        if device.identity.id == device_id:
            return device
    # Not found in live vendor APIs — check registry
    from devices.registry import get_device_by_id

    row = await get_device_by_id(device_id, session)
    if not row:
        return None
    device = _row_to_spire(row)
    # For Shelly devices with a stored IP, fetch live state so online/power fields are accurate
    if row.get("vendor") == "shelly" and row.get("ip_address"):
        from integrations.shelly.client import ShellyController

        try:
            live = await ShellyController(row["ip_address"]).get_state()
            device.connectivity.online = True
            device.state = {"on": live.get("on", False), "power": live.get("power", 0.0)}
        except Exception as exc:
            logger.debug("Shelly live state fetch failed for %s: %s", device_id, exc)
            device.connectivity.online = False
    return device


async def get_saved_devices(
    property_id: str, settings: Settings, session: AsyncSession
) -> list[SpireDevice]:
    """Return devices from the registry for a specific property."""
    if settings.demo_mode:
        from demo.data import (
            demo_device_as_spire,
            get_demo_devices_for_property,
            is_demo_property,
        )

        if is_demo_property(property_id):
            demo_devs = get_demo_devices_for_property(property_id)
            if demo_devs:
                return [_spire_from_flat(demo_device_as_spire(d)) for d in demo_devs]
            # Property has real Supabase devices — fall through to DB query
    from devices.registry import list_devices

    rows = await list_devices(session, property_id=property_id)
    return [_row_to_spire(row) for row in rows]


async def get_all_saved_devices(settings: Settings, session: AsyncSession) -> list[SpireDevice]:
    """Return all devices from the registry across all properties."""
    from devices.registry import list_devices

    rows = await list_devices(session)
    return [_row_to_spire(row) for row in rows]


def _infer_device_type(vendor: str, model: str) -> str:
    """Infer SpireDevice type from vendor and model string."""
    m = model.lower()
    if any(x in m for x in ["plug", "1pm", "2pm", "plusplug", "mini1pm", "em", "mini pm"]):
        return "plug"
    if any(x in m for x in ["dimmer", "rgbw", "light", "bulb", "duo"]):
        return "light"
    if any(x in m for x in ["door", "motion", "sensor", "flood", "uni", "ht", "h&t"]):
        return "sensor"
    if any(x in m for x in ["lock"]):
        return "lock"
    if vendor == "shelly":
        return "plug"
    if vendor in ("govee", "lifx"):
        return "light"
    return "plug"


def _row_to_spire(row: dict[str, Any]) -> SpireDevice:
    """Convert a devices registry row to SpireDevice."""
    vendor = row.get("vendor", "unknown")
    model = row.get("model") or ""
    # Controllability derives from traits; give actuator vendors the on/off
    # commands so saved rows render as controllable as they did before.
    commands = ["turn_on", "turn_off"] if vendor in ("shelly", "matter") else None

    device = SpireDevice.from_vendor(
        vendor=vendor,
        vendor_id=row.get("vendor_id") or row["id"],
        name=row.get("name") or "Unknown Device",
        device_type=_infer_device_type(vendor, model),
        online=False,
        supported_commands=commands,
    )
    device.placement.property_id = row.get("property_id")
    device.placement.room_id = row.get("room_id")
    return device
