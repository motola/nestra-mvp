"""Hikvision Camera API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from dependencies import SettingsDep
from integrations.hikvision.schemas import (
    HikvisionCameraIn,
    HikvisionCameraOut,
    HikvisionStatusResponse,
)

router = APIRouter(prefix="/integrations/hikvision", tags=["property"])

_MOCK_CAMERAS: dict[UUID, HikvisionCameraOut] = {}
_MOCK_INTEGRATIONS: dict[str, UUID] = {}


@router.post("/cameras", response_model=HikvisionCameraOut, status_code=status.HTTP_201_CREATED)
async def add_camera(
    body: HikvisionCameraIn,
    settings: SettingsDep,
) -> HikvisionCameraOut:
    """Add a Hikvision Camera."""
    existing = next(
        (cam for cam in _MOCK_CAMERAS.values() if cam.camera_id == body.camera_id),
        None,
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Camera already added")

    integration_id = _MOCK_INTEGRATIONS.get("hikvision", uuid4())
    if "hikvision" not in _MOCK_INTEGRATIONS:
        _MOCK_INTEGRATIONS["hikvision"] = integration_id

    camera_id = uuid4()
    camera = HikvisionCameraOut(
        id=camera_id,
        property_id=body.property_id,
        camera_id=body.camera_id,
        name=body.name,
        location=body.location,
        is_online=body.is_online,
        stream_url=body.stream_url,
        last_sync=datetime.now(tz=UTC),
        created_at=datetime.now(tz=UTC),
    )
    _MOCK_CAMERAS[camera_id] = camera
    return camera


@router.get("/cameras", response_model=list[HikvisionCameraOut])
async def list_cameras(
    property_id: UUID | None = None,
    settings: SettingsDep | None = None,
) -> list[HikvisionCameraOut]:
    """List Hikvision Cameras."""
    cameras = list(_MOCK_CAMERAS.values())
    if property_id:
        cameras = [cam for cam in cameras if cam.property_id == property_id]
    return cameras


@router.delete("/cameras/{camera_id}", response_model=HikvisionStatusResponse)
async def remove_camera(
    camera_id: UUID,
    settings: SettingsDep,
) -> HikvisionStatusResponse:
    """Remove a camera."""
    if camera_id not in _MOCK_CAMERAS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    camera = _MOCK_CAMERAS.pop(camera_id)
    return HikvisionStatusResponse(message=f"Camera '{camera.name}' removed")
