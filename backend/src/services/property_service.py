"""
Property service — queries Supabase for properties and device counts.
Appends demo properties when DEMO_MODE=true.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from config import Settings
from models.property import Property, PropertyCreate

logger = logging.getLogger(__name__)


def _configured(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


async def _fetch_device_counts(settings: Settings) -> dict[str, int]:
    from services.device_registry import list_devices
    try:
        rows = await list_devices(settings)
        counts: dict[str, int] = {}
        for row in rows:
            pid = row.get("property_id")
            if pid:
                counts[pid] = counts.get(pid, 0) + 1
        return counts
    except Exception as exc:
        logger.warning("Could not fetch device counts: %s", exc)
    return {}


def _row_to_property(row: dict[str, Any], device_count: int = 0, alert_count: int = 0, is_demo: bool = False) -> Property:
    if alert_count == 0:
        status = "all_clear"
    elif alert_count <= 2:
        status = "needs_attention"
    else:
        status = "critical"
    return Property(
        id=row["id"],
        name=row["name"],
        address=row.get("address") or "",
        organisation_id=row.get("organisation_id"),
        device_count=device_count,
        alert_count=alert_count,
        status=status,
        is_demo=is_demo,
    )


def _demo_properties(alert_counts: dict[str, int]) -> list[Property]:
    from demo.data import DEMO_PROPERTIES, get_demo_devices_for_property
    from demo.alerts import DEMO_ALERTS

    demo_alert_counts: dict[str, int] = {}
    for a in DEMO_ALERTS:
        pid = a.get("property_id")
        if pid and not a.get("dismissed"):
            demo_alert_counts[pid] = demo_alert_counts.get(pid, 0) + 1

    result = []
    for p in DEMO_PROPERTIES:
        devices = get_demo_devices_for_property(p["id"])
        ac = demo_alert_counts.get(p["id"], 0)
        result.append(_row_to_property(p, len(devices), ac, is_demo=True))
    return result


async def list_properties(settings: Settings) -> list[Property]:
    from services.alert_service import get_alert_counts

    real_props: list[Property] = []

    if _configured(settings):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{settings.supabase_url}/rest/v1/properties",
                    headers=_headers(settings),
                    params={"order": "name.asc"},
                )
                if r.status_code == 200:
                    rows = r.json()
                    if rows:
                        device_counts, alert_counts = await asyncio.gather(
                            _fetch_device_counts(settings),
                            get_alert_counts(settings),
                        )
                        real_props = [
                            _row_to_property(row, device_counts.get(row["id"], 0), alert_counts.get(row["id"], 0))
                            for row in rows
                        ]
        except Exception as exc:
            logger.error("Supabase list_properties failed: %s", exc)

    if settings.demo_mode:
        return real_props + _demo_properties({})

    return real_props


async def get_property(property_id: str, settings: Settings) -> Property | None:
    from services.alert_service import get_alert_counts

    if settings.demo_mode and property_id.startswith("demo-"):
        from demo.data import DEMO_PROPERTIES, get_demo_devices_for_property
        from demo.alerts import DEMO_ALERTS
        for p in DEMO_PROPERTIES:
            if p["id"] == property_id:
                devices = get_demo_devices_for_property(property_id)
                ac = sum(1 for a in DEMO_ALERTS if a["property_id"] == property_id and not a.get("dismissed"))
                return _row_to_property(p, len(devices), ac, is_demo=True)
        return None

    if not _configured(settings):
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{settings.supabase_url}/rest/v1/properties",
                headers=_headers(settings),
                params={"id": f"eq.{property_id}", "limit": "1"},
            )
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    device_counts, alert_counts = await asyncio.gather(
                        _fetch_device_counts(settings),
                        get_alert_counts(settings),
                    )
                    return _row_to_property(rows[0], device_counts.get(property_id, 0), alert_counts.get(property_id, 0))
    except Exception as exc:
        logger.error("Supabase get_property failed: %s", exc)

    return None


async def create_property(data: PropertyCreate, settings: Settings) -> Property:
    raise NotImplementedError("Property creation not yet implemented")
