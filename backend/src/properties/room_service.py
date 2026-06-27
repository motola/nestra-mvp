"""Room service — CRUD on the rooms table via SQLModel."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.database import Room as DBRoom
from properties.rooms import Room, RoomCreate

logger = logging.getLogger(__name__)

_DEFAULT_ROOM_NAMES = ["Living Room", "Bedroom", "Kitchen", "Bathroom"]


def _normalise_name(name: str) -> str:
    return name.strip().title()


def _to_room(r: DBRoom) -> Room:
    return Room(id=str(r.id), property_id=str(r.property_id), name=r.name, floor=r.floor)


def _to_dict(r: DBRoom) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "property_id": str(r.property_id),
        "name": r.name,
        "floor": r.floor,
    }


async def list_rooms(property_id: str, session: AsyncSession) -> list[Room]:
    stmt = select(DBRoom).where(DBRoom.property_id == uuid.UUID(property_id)).order_by(DBRoom.name)  # type: ignore[arg-type]
    result = await session.execute(stmt)
    return [_to_room(r) for r in result.scalars().all()]


async def get_room_by_id(room_id: str, session: AsyncSession) -> dict[str, Any] | None:
    room = await session.get(DBRoom, uuid.UUID(room_id))
    return _to_dict(room) if room else None


async def create_room(property_id: str, data: RoomCreate, session: AsyncSession) -> Room:
    room = DBRoom(
        property_id=uuid.UUID(property_id),
        name=_normalise_name(data.name),
        floor=data.floor,
    )
    session.add(room)
    await session.flush()
    await session.refresh(room)
    await session.commit()
    return _to_room(room)


async def rename_room(room_id: str, name: str, session: AsyncSession) -> dict[str, Any]:
    room = await session.get(DBRoom, uuid.UUID(room_id))
    if not room:
        raise RuntimeError(f"Room {room_id} not found")
    room.name = _normalise_name(name)
    await session.commit()
    await session.refresh(room)
    return _to_dict(room)


async def delete_room(room_id: str, session: AsyncSession) -> None:
    """Null out device room assignments then delete the room."""
    from services.device_registry import move_devices_to_null_room

    await move_devices_to_null_room(room_id, session)
    await session.execute(sql_delete(DBRoom).where(DBRoom.id == uuid.UUID(room_id)))  # type: ignore[arg-type]
    await session.commit()


async def seed_default_rooms(property_id: str, session: AsyncSession) -> list[Room]:
    created: list[Room] = []
    for name in _DEFAULT_ROOM_NAMES:
        try:
            room = await create_room(property_id, RoomCreate(name=name), session)
            created.append(room)
        except Exception as exc:
            logger.warning("seed_default_rooms: failed to create '%s': %s", name, exc)
    return created
