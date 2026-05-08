"""Room endpoints — rename and delete individual rooms."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.dependencies import SettingsDep
from models.room import Room
from services import room_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rooms", tags=["rooms"])


class RenamePayload(BaseModel):
    name: str


@router.patch("/{room_id}", response_model=Room)
async def rename_room(room_id: str, payload: RenamePayload, settings: SettingsDep) -> Room:
    """Rename a room. Returns 409 if the name already exists in the same property."""
    existing = await room_service.get_room_by_id(room_id, settings)
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Room name cannot be empty")

    property_id = existing.get("property_id", "")
    if property_id:
        siblings = await room_service.list_rooms(property_id, settings)
        if any(r.name.lower() == name.lower() and r.id != room_id for r in siblings):
            raise HTTPException(
                status_code=409,
                detail=f"A room named '{name}' already exists in this property",
            )

    row = await room_service.rename_room(room_id, name, settings)
    return Room(
        id=existing["id"],
        property_id=existing.get("property_id", ""),
        name=row.get("name", name),
        floor=existing.get("floor"),
    )


@router.delete("/{room_id}")
async def delete_room(room_id: str, settings: SettingsDep) -> dict:
    """Move all devices in the room to Unassigned, then permanently delete the room."""
    existing = await room_service.get_room_by_id(room_id, settings)
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    await room_service.delete_room(room_id, settings)
    return {"deleted": room_id}
