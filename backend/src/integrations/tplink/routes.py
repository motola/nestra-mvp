"""TP-Link Smart Plug API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from dependencies import SettingsDep
from integrations.tplink.schemas import (
    TPlinkPlugIn,
    TPlinkPlugOut,
    TPlinkPowerStateUpdate,
    TPlinkStatusResponse,
)

router = APIRouter(prefix="/integrations/tplink", tags=["property"])

_MOCK_PLUGS: dict[UUID, TPlinkPlugOut] = {}
_MOCK_INTEGRATIONS: dict[str, UUID] = {}


@router.post("/plugs", response_model=TPlinkPlugOut, status_code=status.HTTP_201_CREATED)
async def add_plug(
    body: TPlinkPlugIn,
    settings: SettingsDep,
) -> TPlinkPlugOut:
    """Add a TP-Link Smart Plug."""
    existing = next(
        (plug for plug in _MOCK_PLUGS.values() if plug.device_id == body.device_id),
        None,
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plug already added")

    integration_id = _MOCK_INTEGRATIONS.get("tplink", uuid4())
    if "tplink" not in _MOCK_INTEGRATIONS:
        _MOCK_INTEGRATIONS["tplink"] = integration_id

    plug_id = uuid4()
    plug = TPlinkPlugOut(
        id=plug_id,
        property_id=body.property_id,
        device_id=body.device_id,
        name=body.name,
        power_state=body.power_state,
        power_usage_w=body.power_usage_w,
        is_online=True,
        last_sync=datetime.now(tz=UTC),
        created_at=datetime.now(tz=UTC),
    )
    _MOCK_PLUGS[plug_id] = plug
    return plug


@router.get("/plugs", response_model=list[TPlinkPlugOut])
async def list_plugs(
    property_id: UUID | None = None,
    settings: SettingsDep | None = None,
) -> list[TPlinkPlugOut]:
    """List TP-Link Smart Plugs."""
    plugs = list(_MOCK_PLUGS.values())
    if property_id:
        plugs = [plug for plug in plugs if plug.property_id == property_id]
    return plugs


@router.post("/plugs/{plug_id}/power", response_model=TPlinkStatusResponse)
async def set_power_state(
    plug_id: UUID,
    body: TPlinkPowerStateUpdate,
    settings: SettingsDep,
) -> TPlinkStatusResponse:
    """Set power state (on/off)."""
    if plug_id not in _MOCK_PLUGS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plug not found")

    plug = _MOCK_PLUGS[plug_id]
    plug.power_state = body.power_state
    plug.last_sync = datetime.now(tz=UTC)
    _MOCK_PLUGS[plug_id] = plug

    state = "ON" if body.power_state else "OFF"
    return TPlinkStatusResponse(message=f"Plug '{plug.name}' turned {state}")


@router.delete("/plugs/{plug_id}", response_model=TPlinkStatusResponse)
async def remove_plug(
    plug_id: UUID,
    settings: SettingsDep,
) -> TPlinkStatusResponse:
    """Remove a plug."""
    if plug_id not in _MOCK_PLUGS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plug not found")

    plug = _MOCK_PLUGS.pop(plug_id)
    return TPlinkStatusResponse(message=f"Plug '{plug.name}' removed")
