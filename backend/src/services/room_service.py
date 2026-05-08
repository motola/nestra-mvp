"""Room service — seed data + Supabase CRUD."""
from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from config import Settings
from models.room import Room, RoomCreate

logger = logging.getLogger(__name__)

_SEED: list[dict[str, Any]] = [
    {"id": "room-001", "property_id": "prop-001", "name": "Living Room", "floor": 0},
    {"id": "room-002", "property_id": "prop-001", "name": "Bedroom", "floor": 1},
    {"id": "room-003", "property_id": "prop-001", "name": "Kitchen", "floor": 0},
    {"id": "room-004", "property_id": "prop-002", "name": "Living Room", "floor": 0},
    {"id": "room-005", "property_id": "prop-002", "name": "Bedroom", "floor": 1},
    {"id": "room-006", "property_id": "prop-002", "name": "Kitchen", "floor": 0},
    {"id": "room-007", "property_id": "prop-003", "name": "Living Room", "floor": 0},
    {"id": "room-008", "property_id": "prop-003", "name": "Bedroom", "floor": 1},
    {"id": "room-009", "property_id": "prop-003", "name": "Kitchen", "floor": 0},
]


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


async def list_rooms(property_id: str, settings: Settings) -> list[Room]:
    if not _configured(settings):
        return [Room(**r) for r in _SEED if r["property_id"] == property_id]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _base_url(settings),
                headers=_headers(settings),
                params={"property_id": f"eq.{property_id}", "order": "name.asc"},
            )
            if r.status_code == 200:
                return [Room(**row) for row in r.json()]
            logger.warning("Supabase list_rooms %s: %s", r.status_code, r.text[:200])
    except Exception as exc:
        logger.error("Supabase list_rooms failed: %s", exc)

    return [Room(**r) for r in _SEED if r["property_id"] == property_id]


async def create_room(property_id: str, data: RoomCreate, settings: Settings) -> Room:
    room = Room(id=str(uuid.uuid4()), property_id=property_id, **data.model_dump())

    if not _configured(settings):
        return room

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            _base_url(settings),
            headers={**_headers(settings), "Prefer": "return=representation"},
            json=room.model_dump(),
        )
        r.raise_for_status()
        created = r.json()
        row = created[0] if isinstance(created, list) else created
        return Room(**row)
