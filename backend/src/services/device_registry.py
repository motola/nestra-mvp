"""
Device registry — CRUD on the Supabase devices table via PostgREST.

Uses SUPABASE_URL/rest/v1/devices with the service role key.
No asyncpg required — plain HTTPS via httpx.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from config import Settings

logger = logging.getLogger(__name__)


def _base_url(settings: Settings) -> str:
    return f"{settings.supabase_url}/rest/v1/devices"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _configured(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


async def list_devices(
    settings: Settings,
    property_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return devices from Supabase, newest first. Optionally filter by property_id."""
    if not _configured(settings):
        return []
    try:
        params: dict[str, str] = {"order": "created_at.desc"}
        if property_id:
            params["property_id"] = f"eq.{property_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params=params,
            )
            if r.status_code == 200:
                return r.json()
            logger.warning("Supabase list_devices %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("Supabase list_devices failed: %s", exc)
    return []


async def save_device(data: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Insert a device row and return the created record."""
    if not _configured(settings):
        raise RuntimeError("Supabase not configured — add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to .env")

    row = {
        "id": str(uuid.uuid4()),
        "property_id": data.get("property_id") or None,
        "room_id": data.get("room_id") or None,
        "vendor": data["vendor"],
        "vendor_id": data.get("vendor_id") or data.get("mac") or "",
        "name": data["name"],
        "model": data.get("model") or "",
        "ip_address": data.get("ip") or "",
        "mac": data.get("mac") or "",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            _base_url(settings),
            headers={**_headers(settings), "Prefer": "return=representation"},
            json=row,
        )
        r.raise_for_status()
        created = r.json()
        return created[0] if isinstance(created, list) else created


async def get_device_by_id(device_id: str, settings: Settings) -> dict[str, Any] | None:
    """Return a single device row by its UUID, or None if not found."""
    if not _configured(settings):
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={"id": f"eq.{device_id}", "limit": "1"},
            )
            if r.status_code == 200:
                rows = r.json()
                return rows[0] if rows else None
            logger.warning("Supabase get_device_by_id %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("Supabase get_device_by_id failed: %s", exc)
    return None


async def update_device(device_id: str, data: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Partially update a device row and return the updated record."""
    if not _configured(settings):
        raise RuntimeError("Supabase not configured")

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.patch(
            _base_url(settings),
            headers={**_headers(settings), "Prefer": "return=representation"},
            params={"id": f"eq.{device_id}"},
            json=data,
        )
        r.raise_for_status()
        rows = r.json()
        return rows[0] if isinstance(rows, list) and rows else data


async def delete_device(device_id: str, settings: Settings) -> None:
    """Delete a device row by its UUID."""
    if not _configured(settings):
        raise RuntimeError("Supabase not configured")

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(
            _base_url(settings),
            headers=_headers(settings),
            params={"id": f"eq.{device_id}"},
        )
        r.raise_for_status()
