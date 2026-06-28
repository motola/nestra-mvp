"""Property endpoints — portfolio, property detail, room management, and property deletion."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from api.dependencies import SessionDep, SettingsDep
from devices import service as device_service
from properties import room_service
from properties import service as property_service
from properties.models import Property
from properties.rooms import Room, RoomCreate
from shared.pagination import PageDep, paginate

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/", response_model=list[Property])
async def list_properties(
    settings: SettingsDep, session: SessionDep, page: PageDep
) -> list[Property]:
    """Return the org's properties. Supports ?limit/?offset."""
    return paginate(await property_service.list_properties(session, settings), page)


@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: str, settings: SettingsDep, session: SessionDep) -> Property:
    prop = await property_service.get_property(property_id, session, settings)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.delete("/{property_id}")
async def delete_property(
    property_id: str, settings: SettingsDep, session: SessionDep
) -> dict[str, Any]:
    """Permanently delete a property and all its rooms, devices, and state history."""
    prop = await property_service.get_property(property_id, session, settings)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    try:
        await property_service.delete_property(property_id, session)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"deleted": property_id}


@router.get("/{property_id}/rooms", response_model=list[Room])
async def list_property_rooms(property_id: str, session: SessionDep) -> list[Room]:
    return await room_service.list_rooms(property_id, session)


@router.post("/{property_id}/rooms", response_model=Room, status_code=201)
async def create_property_room(property_id: str, data: RoomCreate, session: SessionDep) -> Room:
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Room name cannot be empty")

    existing_rooms = await room_service.list_rooms(property_id, session)
    if any(r.name.lower() == name.lower() for r in existing_rooms):
        raise HTTPException(
            status_code=409,
            detail=f"A room named '{name}' already exists in this property",
        )

    from properties.rooms import RoomCreate as RC

    return await room_service.create_room(property_id, RC(name=name, floor=data.floor), session)


@router.get("/{property_id}/devices", response_model=list[dict[str, Any]])
async def list_property_devices(
    property_id: str, settings: SettingsDep, session: SessionDep
) -> list[dict[str, Any]]:
    devices = await device_service.get_saved_devices(property_id, settings, session)
    return [d.to_api() for d in devices]
