"""Property endpoints — portfolio, property detail, and room management."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.dependencies import SettingsDep
from models.device import AlphaconDevice
from models.property import Property
from models.room import Room, RoomCreate
from services import device_service, property_service, room_service

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/", response_model=list[Property])
async def list_properties(settings: SettingsDep) -> list[Property]:
    return await property_service.list_properties(settings)


@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: str, settings: SettingsDep) -> Property:
    prop = await property_service.get_property(property_id, settings)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.get("/{property_id}/rooms", response_model=list[Room])
async def list_property_rooms(property_id: str, settings: SettingsDep) -> list[Room]:
    if settings.demo_mode and property_id.startswith("demo-"):
        from demo.data import get_demo_rooms
        return [Room(**r) for r in get_demo_rooms(property_id)]
    return await room_service.list_rooms(property_id, settings)


@router.post("/{property_id}/rooms", response_model=Room, status_code=201)
async def create_property_room(
    property_id: str, data: RoomCreate, settings: SettingsDep
) -> Room:
    return await room_service.create_room(property_id, data, settings)


@router.get("/{property_id}/devices", response_model=list[AlphaconDevice])
async def list_property_devices(
    property_id: str, settings: SettingsDep
) -> list[AlphaconDevice]:
    return await device_service.get_saved_devices(property_id, settings)
