"""Room service — Supabase CRUD."""
from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from config import Settings
from models.room import Room, RoomCreate

logger = logging.getLogger(__name__)

_DEFAULT_ROOM_NAMES = ["Living Room", "Bedroom", "Kitchen", "Bathroom"]


def _normalise_name(name: str) -> str:
    return name.strip().title()


def _configured(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def _base_url(settings: Settings) -> str:
    return f"{settings.supabase_url}/rest/v1/rooms"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _row_to_room(row: dict[str, Any]) -> Room:
    return Room(
        id=row["id"],
        property_id=row["property_id"],
        name=row["name"],
        floor=row.get("floor"),
    )


async def list_rooms(property_id: str, settings: Settings) -> list[Room]:
    if not _configured(settings):
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={"property_id": f"eq.{property_id}", "order": "name.asc"},
            )
            if r.status_code == 200:
                return [_row_to_room(row) for row in r.json()]
            logger.warning("Supabase list_rooms %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("Supabase list_rooms failed: %s", exc)

    return []


async def get_room_by_id(room_id: str, settings: Settings) -> dict[str, Any] | None:
    if not _configured(settings):
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={"id": f"eq.{room_id}", "limit": "1"},
            )
            if r.status_code == 200:
                rows = r.json()
                return rows[0] if rows else None
            logger.warning("get_room_by_id %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("get_room_by_id failed: %s", exc)
    return None


async def create_room(property_id: str, data: RoomCreate, settings: Settings) -> Room:
    room_id = str(uuid.uuid4())

    if not _configured(settings):
        return Room(id=room_id, property_id=property_id, name=data.name, floor=data.floor)

    # Only send columns that exist in the DB — not device_count or alert_count
    db_row: dict[str, Any] = {
        "id": room_id,
        "property_id": property_id,
        "name": _normalise_name(data.name),
    }
    if data.floor is not None:
        db_row["floor"] = data.floor

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            _base_url(settings),
            headers={**_headers(settings), "Prefer": "return=representation"},
            json=db_row,
        )
        r.raise_for_status()
        rows = r.json()
        row = (rows[0] if isinstance(rows, list) else rows) or db_row
        return _row_to_room({**db_row, **row})


async def rename_room(room_id: str, name: str, settings: Settings) -> dict[str, Any]:
    if not _configured(settings):
        raise RuntimeError("Supabase not configured")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.patch(
            _base_url(settings),
            headers={**_headers(settings), "Prefer": "return=representation"},
            params={"id": f"eq.{room_id}"},
            json={"name": _normalise_name(name)},
        )
        r.raise_for_status()
        rows = r.json()
        return rows[0] if isinstance(rows, list) and rows else {"id": room_id, "name": name}


async def delete_room(room_id: str, settings: Settings) -> None:
    """Move all devices in the room to Unassigned, then delete the room."""
    if not _configured(settings):
        return
    from services.device_registry import move_devices_to_null_room
    await move_devices_to_null_room(room_id, settings)
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(
            _base_url(settings),
            headers=_headers(settings),
            params={"id": f"eq.{room_id}"},
        )
        if r.status_code not in (200, 204):
            logger.warning("delete_room %s: %s", r.status_code, r.text[:200])


async def seed_default_rooms(property_id: str, settings: Settings) -> list[Room]:
    """Create default rooms for a newly created property."""
    created: list[Room] = []
    for name in _DEFAULT_ROOM_NAMES:
        try:
            room = await create_room(property_id, RoomCreate(name=name), settings)
            created.append(room)
        except Exception as exc:
            logger.warning("seed_default_rooms: failed to create '%s': %s", name, exc)
    return created
