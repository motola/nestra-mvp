"""
Alert service — stores and queries alerts in Supabase.

alert_service detects anomalies when device state is checked and persists
them to the alerts table via PostgREST.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from config import Settings
from models.alert import Alert

logger = logging.getLogger(__name__)


def _base_url(settings: Settings) -> str:
    return f"{settings.supabase_url}/rest/v1/alerts"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _configured(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def _row_to_alert(row: dict[str, Any]) -> Alert:
    return Alert(
        id=row["id"],
        device_id=row.get("device_id", ""),
        device_name=row.get("device_name", "Unknown Device"),
        property_id=row.get("property_id", ""),
        property_name=row.get("property_name", ""),
        type=row.get("type", "unknown"),
        severity=row.get("severity", "info"),
        message=row.get("message", ""),
        created_at=row.get("created_at", ""),
        dismissed=row.get("dismissed", False),
    )


async def list_active_alerts(settings: Settings) -> list[Alert]:
    """Return all non-dismissed alerts, newest first."""
    if not _configured(settings):
        return []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={"dismissed": "eq.false", "order": "created_at.desc"},
            )
            if r.status_code == 200:
                return [_row_to_alert(row) for row in r.json()]
            logger.warning("list_active_alerts %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("list_active_alerts failed: %s", exc)
    return []


async def dismiss_alert(alert_id: str, settings: Settings) -> None:
    """Mark an alert row as dismissed."""
    if not _configured(settings):
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.patch(
                _base_url(settings),
                headers=_headers(settings),
                params={"id": f"eq.{alert_id}"},
                json={"dismissed": True},
            )
            if r.status_code not in (200, 204):
                logger.warning("dismiss_alert %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("dismiss_alert failed: %s", exc)


async def get_alert_counts(settings: Settings) -> dict[str, int]:
    """Return {property_id: active_alert_count} for all properties."""
    if not _configured(settings):
        return {}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={"dismissed": "eq.false", "select": "property_id"},
            )
            if r.status_code == 200:
                counts: dict[str, int] = {}
                for row in r.json():
                    pid = row.get("property_id")
                    if pid:
                        counts[pid] = counts.get(pid, 0) + 1
                return counts
    except Exception as exc:
        logger.error("get_alert_counts failed: %s", exc)
    return {}


async def create_alert(
    device_id: str,
    device_name: str,
    property_id: str,
    property_name: str,
    alert_type: str,
    severity: str,
    message: str,
    settings: Settings,
) -> None:
    """Insert a new alert row. Silently skips if Supabase is not configured."""
    if not _configured(settings):
        return
    try:
        row = {
            "id": str(uuid.uuid4()),
            "device_id": device_id,
            "device_name": device_name,
            "property_id": property_id,
            "property_name": property_name,
            "type": alert_type,
            "severity": severity,
            "message": message,
            "dismissed": False,
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                _base_url(settings),
                headers=_headers(settings),
                json=row,
            )
            if r.status_code not in (200, 201):
                logger.warning("create_alert %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.warning("create_alert failed: %s", exc)
