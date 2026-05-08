"""Device endpoints — live vendor devices and Supabase registry."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.dependencies import SettingsDep
from models.device import AlphaconDevice
from services import device_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/saved", response_model=list[AlphaconDevice])
async def list_saved_devices(settings: SettingsDep) -> list[AlphaconDevice]:
    """Return all devices from the Supabase registry (no live vendor API calls)."""
    return await device_service.get_all_saved_devices(settings)


@router.get("/", response_model=list[AlphaconDevice])
async def list_devices(settings: SettingsDep) -> list[AlphaconDevice]:
    """Return all devices across all configured vendor integrations."""
    return await device_service.list_all_devices(settings)


# ── Matter device control (must be declared before /{device_id}) ──────────────

class MatterCommandPayload(BaseModel):
    command: str  # "on_off" | "brightness" | "color_temperature"
    value: Any = None


async def _resolve_matter_node_id(device_id: str, settings: SettingsDep) -> str:
    from services.device_registry import get_device_by_id
    row = await get_device_by_id(device_id, settings)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    node_id = row.get("vendor_id")
    if not node_id:
        raise HTTPException(status_code=422, detail="Device has no Matter node ID")
    return node_id


@router.post("/matter/{device_id}/command")
async def matter_command(
    device_id: str, payload: MatterCommandPayload, settings: SettingsDep
) -> dict:
    """Send an on/off, brightness, or color_temperature command to a Matter device."""
    from integrations.matter.server import MatterServerClient

    node_id = await _resolve_matter_node_id(device_id, settings)

    try:
        async with MatterServerClient() as client:
            if payload.command == "on_off":
                cmd = "on" if payload.value else "off"
                result = await client.send_command(node_id, 1, 6, cmd, {})
            elif payload.command == "brightness":
                result = await client.send_command(node_id, 1, 8, "move_to_level", {
                    "Level": int(payload.value),
                    "TransitionTime": 0,
                    "OptionsMask": 0,
                    "OptionsOverride": 0,
                })
            elif payload.command == "color_temperature":
                result = await client.send_command(node_id, 1, 768, "move_to_color_temperature", {
                    "ColorTemperatureMireds": int(payload.value),
                    "TransitionTime": 0,
                    "OptionsMask": 0,
                    "OptionsOverride": 0,
                })
            else:
                raise HTTPException(status_code=400, detail=f"Unknown command: {payload.command}")
    except HTTPException:
        raise
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return result or {"ok": True}


@router.get("/matter/{device_id}/state")
async def matter_device_state(device_id: str, settings: SettingsDep) -> dict:
    """Return the current attribute state for a Matter device from the server's cache."""
    from integrations.matter.server import MatterServerClient

    node_id = await _resolve_matter_node_id(device_id, settings)

    try:
        async with MatterServerClient() as client:
            node = await client.get_node(node_id)
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if not node:
        raise HTTPException(status_code=404, detail="Matter node not found on server")

    attrs: dict = node.get("attributes") or {}

    on_off = None
    brightness = None
    for ep in ("1", "0"):
        ep_attrs = attrs.get(ep, {})
        c6 = ep_attrs.get("6", {})
        if c6:
            on_off = c6.get("OnOff", c6.get("0"))
            break
    for ep in ("1", "0"):
        ep_attrs = attrs.get(ep, {})
        c8 = ep_attrs.get("8", {})
        if c8:
            brightness = c8.get("CurrentLevel", c8.get("0"))
            break

    return {
        "device_id": device_id,
        "node_id": node_id,
        "online": node.get("available", False),
        "on_off": on_off,
        "brightness": brightness,
    }


# ── Shelly local control ──────────────────────────────────────────────────────

class ControlPayload(BaseModel):
    command: str  # "turn_on" | "turn_off"
    value: Any = None


@router.post("/{device_id}/control")
async def control_device(
    device_id: str, payload: ControlPayload, settings: SettingsDep
) -> dict:
    """Send turn_on / turn_off to a Shelly device using its saved IP address."""
    if settings.demo_mode:
        from demo.data import is_demo_device
        if is_demo_device(device_id):
            return {"success": True, "state": payload.command == "turn_on"}

    from services.device_registry import get_device_by_id
    from services.state_history_service import record_state_change
    from integrations.shelly_local.controller import ShellyLocalController

    row = await get_device_by_id(device_id, settings)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    ip = row.get("ip_address") or ""
    if not ip:
        raise HTTPException(status_code=422, detail="Device has no IP address stored")

    ctrl = ShellyLocalController(ip)
    try:
        if payload.command == "turn_on":
            ok = await ctrl.turn_on()
            event_type = "turned_on"
        elif payload.command == "turn_off":
            ok = await ctrl.turn_off()
            event_type = "turned_off"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown command: {payload.command}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if ok:
        await record_state_change(
            device_id=device_id,
            event_type=event_type,
            settings=settings,
            property_id=row.get("property_id"),
        )

    return {"success": ok, "state": payload.command == "turn_on"}


@router.get("/{device_id}/state")
async def device_state(device_id: str, settings: SettingsDep) -> dict:
    """Return live on/off + power draw for a locally-reachable Shelly device."""
    if settings.demo_mode:
        from demo.data import is_demo_device, get_demo_device, demo_device_state as _demo_state
        if is_demo_device(device_id):
            d = get_demo_device(device_id)
            if not d:
                raise HTTPException(status_code=404, detail="Device not found")
            return _demo_state(d)

    from services.device_registry import get_device_by_id
    from services.state_history_service import record_state_change
    from integrations.shelly_local.controller import ShellyLocalController

    row = await get_device_by_id(device_id, settings)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    ip = row.get("ip_address") or ""
    if not ip:
        raise HTTPException(status_code=422, detail="Device has no IP address stored")

    try:
        state = await ShellyLocalController(ip).get_state()
    except Exception as exc:
        await record_state_change(
            device_id=device_id,
            event_type="went_offline",
            settings=settings,
            property_id=row.get("property_id"),
        )
        raise HTTPException(status_code=502, detail=str(exc))

    await record_state_change(
        device_id=device_id,
        event_type="power_reading",
        settings=settings,
        property_id=row.get("property_id"),
        value=str(state["power"]),
    )

    return {"device_id": device_id, "online": True, **state}


@router.get("/{device_id}/power-history")
async def device_power_history(device_id: str, settings: SettingsDep) -> list[dict]:
    """Return power readings for the last 24 hours for charting."""
    if settings.demo_mode:
        from demo.data import is_demo_device
        if is_demo_device(device_id):
            from demo.history import get_demo_power_history
            return get_demo_power_history(device_id)
    from services.state_history_service import get_power_history
    return await get_power_history(device_id, settings)


@router.get("/{device_id}/history")
async def device_history(device_id: str, settings: SettingsDep) -> list[dict]:
    """Return the last 50 state change events for a device, newest first."""
    if settings.demo_mode:
        from demo.data import is_demo_device
        if is_demo_device(device_id):
            from demo.history import get_demo_history
            return get_demo_history(device_id, limit=50)
    from services.state_history_service import get_device_history
    return await get_device_history(device_id, settings, limit=50)


# ── Room assignment ───────────────────────────────────────────────────────────

class AssignRoomPayload(BaseModel):
    room_id: str | None


@router.patch("/{device_id}")
async def assign_device_room(
    device_id: str, payload: AssignRoomPayload, settings: SettingsDep
) -> dict:
    """Update a device's room assignment. Validates the room belongs to the same property."""
    from services.device_registry import get_device_by_id, assign_device_room as _assign
    from services.room_service import get_room_by_id

    device_row = await get_device_by_id(device_id, settings)
    if not device_row:
        raise HTTPException(status_code=404, detail="Device not found")

    if payload.room_id is not None:
        room_row = await get_room_by_id(payload.room_id, settings)
        if not room_row:
            raise HTTPException(status_code=404, detail="Room not found")
        if room_row.get("property_id") != device_row.get("property_id"):
            raise HTTPException(
                status_code=422,
                detail="Cannot move device to a room in a different property",
            )

    return await _assign(device_id, payload.room_id, settings)


# ── Delete device ─────────────────────────────────────────────────────────────

@router.delete("/{device_id}")
async def delete_device_endpoint(device_id: str, settings: SettingsDep) -> dict:
    """Delete a device and its state history from the registry."""
    from services.device_registry import get_device_by_id, delete_device
    from services.state_history_service import delete_device_history

    row = await get_device_by_id(device_id, settings)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")

    try:
        await delete_device_history(device_id, settings)
    except Exception as exc:
        logger.warning("Could not delete state history for %s: %s", device_id, exc)

    await delete_device(device_id, settings)
    return {"deleted": device_id}


# ── Generic device lookup ─────────────────────────────────────────────────────

@router.get("/{device_id}", response_model=AlphaconDevice)
async def get_device(device_id: str, settings: SettingsDep) -> AlphaconDevice:
    """Return current state for a single device by its Alphacon ID."""
    device = await device_service.get_device(device_id, settings)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
