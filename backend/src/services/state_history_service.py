"""State history service — records and queries device state change events."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from config import Settings

logger = logging.getLogger(__name__)


def _base_url(settings: Settings) -> str:
    return f"{settings.supabase_url}/rest/v1/state_history"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _configured(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


async def record_state_change(
    device_id: str,
    event_type: str,
    settings: Settings,
    property_id: str | None = None,
    value: str | None = None,
) -> None:
    """Insert a state change event row. Silently skips if Supabase is not configured."""
    if not _configured(settings):
        return
    try:
        row: dict[str, Any] = {
            "device_id": device_id,
            "event_type": event_type,
        }
        if property_id:
            row["property_id"] = property_id
        if value is not None:
            row["value"] = value

        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                _base_url(settings),
                headers=_headers(settings),
                json=row,
            )
            if r.status_code not in (200, 201):
                logger.warning("state_history insert %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.warning("record_state_change failed for %s: %s", device_id, exc)


async def get_power_history(
    device_id: str,
    settings: Settings,
) -> list[dict[str, Any]]:
    """Return power readings for the last 24 hours, oldest first, for charting."""
    if not _configured(settings):
        return []
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={
                    "device_id": f"eq.{device_id}",
                    "event_type": "eq.power_reading",
                    "recorded_at": f"gte.{since}",
                    "order": "recorded_at.asc",
                    "select": "recorded_at,value",
                    "limit": "1440",
                },
            )
            if r.status_code == 200:
                return r.json()
            logger.warning("get_power_history %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("get_power_history failed: %s", exc)
    return []


async def delete_device_history(device_id: str, settings: Settings) -> None:
    """Delete all state history rows for a device. Silently skips if Supabase not configured."""
    if not _configured(settings):
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.delete(
                _base_url(settings),
                headers=_headers(settings),
                params={"device_id": f"eq.{device_id}"},
            )
            if r.status_code not in (200, 204):
                logger.warning("delete_device_history %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.warning("delete_device_history failed for %s: %s", device_id, exc)


async def get_device_history(
    device_id: str,
    settings: Settings,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return state history events for a device, newest first. Excludes power readings."""
    if not _configured(settings):
        return []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={
                    "device_id": f"eq.{device_id}",
                    "event_type": "neq.power_reading",
                    "order": "recorded_at.desc",
                    "limit": str(limit),
                },
            )
            if r.status_code == 200:
                return r.json()
            logger.warning("get_device_history %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("get_device_history failed: %s", exc)
    return []
