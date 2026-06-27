"""
Device service — polls all configured vendor adapters and aggregates results.

This is the single entry point for device data across the platform.
It knows about vendor adapters; the API layer does not.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from devices.models import AlphaconDevice

logger = logging.getLogger(__name__)


async def list_all_devices(settings: Settings, session: AsyncSession) -> list[AlphaconDevice]:
    """
    Return all devices: demo data (if demo mode), cloud vendor APIs,
    and saved registry devices (Shelly, Matter from the database).
    """
    devices: list[AlphaconDevice] = []

    if settings.demo_mode:
        from demo.data import DEMO_DEVICES, demo_device_as_alphacon

        devices.extend([AlphaconDevice(**demo_device_as_alphacon(d)) for d in DEMO_DEVICES])

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
        devices.extend([_row_to_alphacon(row) for row in rows])
        logger.info("Registry: fetched %d saved devices", len(rows))
    except Exception as exc:
        logger.error("Registry device list failed: %s", exc)

    return devices


async def get_device(
    device_id: str, settings: Settings, session: AsyncSession
) -> AlphaconDevice | None:
    """Return current state for a single device. Checks vendor APIs first, falls back to DB."""
    if settings.demo_mode:
        from demo.data import demo_device_as_alphacon, get_demo_device, is_demo_device

        if is_demo_device(device_id):
            d = get_demo_device(device_id)
            return AlphaconDevice(**demo_device_as_alphacon(d)) if d else None

    all_devices = await list_all_devices(settings, session)
    for device in all_devices:
        if device.id == device_id:
            return device
    # Not found in live vendor APIs — check registry
    from devices.registry import get_device_by_id

    row = await get_device_by_id(device_id, session)
    if not row:
        return None
    device = _row_to_alphacon(row)
    # For Shelly devices with a stored IP, fetch live state so online/power fields are accurate
    if row.get("vendor") == "shelly" and row.get("ip_address"):
        from integrations.shelly_local.controller import ShellyLocalController

        try:
            live = await ShellyLocalController(row["ip_address"]).get_state()
            device.online = True
            device.controllable = True
            device.power_draw = live.get("power")
            device.state = {"on": live.get("on", False), "power": live.get("power", 0.0)}
        except Exception as exc:
            logger.debug("Shelly live state fetch failed for %s: %s", device_id, exc)
            device.online = False
    return device


async def get_saved_devices(
    property_id: str, settings: Settings, session: AsyncSession
) -> list[AlphaconDevice]:
    """Return devices from the registry for a specific property."""
    if settings.demo_mode:
        from demo.data import (
            demo_device_as_alphacon,
            get_demo_devices_for_property,
            is_demo_property,
        )

        if is_demo_property(property_id):
            demo_devs = get_demo_devices_for_property(property_id)
            if demo_devs:
                return [AlphaconDevice(**demo_device_as_alphacon(d)) for d in demo_devs]
            # Property has real Supabase devices — fall through to DB query
    from devices.registry import list_devices

    rows = await list_devices(session, property_id=property_id)
    return [_row_to_alphacon(row) for row in rows]


async def get_all_saved_devices(settings: Settings, session: AsyncSession) -> list[AlphaconDevice]:
    """Return all devices from the registry across all properties."""
    from devices.registry import list_devices

    rows = await list_devices(session)
    return [_row_to_alphacon(row) for row in rows]


def _infer_device_type(vendor: str, model: str) -> str:
    """Infer AlphaconDevice type from vendor and model string."""
    m = model.lower()
    if any(x in m for x in ["plug", "1pm", "2pm", "plusplug", "mini1pm", "em", "mini pm"]):
        return "plug"
    if any(x in m for x in ["dimmer", "rgbw", "light", "bulb", "duo"]):
        return "light"
    if any(x in m for x in ["door", "motion", "sensor", "flood", "uni", "ht", "h&t"]):
        return "sensor"
    if any(x in m for x in ["lock"]):
        return "lock"
    if vendor in ("shelly", "shelly_local"):
        return "plug"
    if vendor in ("govee", "lifx"):
        return "light"
    return "plug"


def _row_to_alphacon(row: dict[str, Any]) -> AlphaconDevice:
    """Convert a devices registry row to AlphaconDevice."""
    vendor = row.get("vendor", "unknown")
    model = row.get("model") or ""
    created = row.get("created_at")
    try:
        last_seen = datetime.fromisoformat(created) if created else datetime.now(UTC)
    except ValueError:
        last_seen = datetime.now(UTC)

    return AlphaconDevice(
        id=row["id"],
        vendor_id=row.get("vendor_id") or row["id"],
        vendor=vendor,
        name=row.get("name") or "Unknown Device",
        type=_infer_device_type(vendor, model),
        online=False,
        controllable=vendor in ("shelly", "shelly_local", "matter"),
        property_id=row.get("property_id"),
        room_id=row.get("room_id"),
        last_seen=last_seen,
    )
