"""Device endpoints — live vendor devices and database registry."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import SessionDep, SettingsDep
from devices import service as device_service
from devices.schemas import (
    AssignRoomPayload,
    ControlPayload,
    DeleteResult,
    DeviceCommandResult,
    DeviceResponse,
    MatterCommandPayload,
    MatterDeviceState,
)
from shared.pagination import PageDep, paginate

if TYPE_CHECKING:
    from integrations.matter.server import MatterServerClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/saved", response_model=list[DeviceResponse])
async def list_saved_devices(
    settings: SettingsDep, session: SessionDep, page: PageDep
) -> list[dict[str, Any]]:
    """Return devices from the registry (no live vendor API calls). Supports ?limit/?offset."""
    devices = await device_service.get_all_saved_devices(settings, session)
    return [d.to_api() for d in paginate(devices, page)]


@router.get("/", response_model=list[DeviceResponse])
async def list_devices(
    settings: SettingsDep, session: SessionDep, page: PageDep
) -> list[dict[str, Any]]:
    """Return devices across all configured vendor integrations. Supports ?limit/?offset."""
    devices = await device_service.list_all_devices(settings, session)
    return [d.to_api() for d in paginate(devices, page)]


# ── Matter device control (must be declared before /{device_id}) ──────────────

# Matter transition options shared by level/colour commands.
_MATTER_TRANSITION = {"TransitionTime": 0, "OptionsMask": 0, "OptionsOverride": 0}


async def _resolve_matter_node_id(device_id: str, session: AsyncSession) -> str:
    from devices.registry import get_device_by_id

    row = await get_device_by_id(device_id, session)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    node_id = row.get("vendor_id")
    if not node_id:
        raise HTTPException(status_code=422, detail="Device has no Matter node ID")
    return str(node_id)


async def _dispatch_matter_command(
    client: MatterServerClient, node_id: str, payload: MatterCommandPayload
) -> dict[str, Any]:
    """Translate a high-level command into the matching Matter cluster command."""
    if payload.command == "on_off":
        return await client.send_command(node_id, 1, 6, "on" if payload.value else "off", {})
    if payload.command == "brightness":
        args = {"Level": int(payload.value), **_MATTER_TRANSITION}
        return await client.send_command(node_id, 1, 8, "move_to_level", args)
    if payload.command == "color_temperature":
        args = {"ColorTemperatureMireds": int(payload.value), **_MATTER_TRANSITION}
        return await client.send_command(node_id, 1, 768, "move_to_color_temperature", args)
    raise HTTPException(status_code=400, detail=f"Unknown command: {payload.command}")


@router.post("/matter/{device_id}/command")
async def matter_command(
    device_id: str, payload: MatterCommandPayload, session: SessionDep
) -> dict[str, Any]:
    """Send an on/off, brightness, or color_temperature command to a Matter device.

    The result is the Matter server's raw response, so it stays untyped.
    """
    from integrations.matter.server import MatterServerClient

    node_id = await _resolve_matter_node_id(device_id, session)
    try:
        async with MatterServerClient() as client:
            result = await _dispatch_matter_command(client, node_id, payload)
    except HTTPException:
        raise
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return result or {"ok": True}


def _read_cluster_attr(attrs: dict[str, Any], cluster: str, name: str) -> Any:
    """Read a Matter cluster attribute, trying endpoint 1 then 0, name then index 0."""
    for endpoint in ("1", "0"):
        cluster_attrs = attrs.get(endpoint, {}).get(cluster, {})
        if cluster_attrs:
            return cluster_attrs.get(name, cluster_attrs.get("0"))
    return None


@router.get("/matter/{device_id}/state", response_model=MatterDeviceState)
async def matter_device_state(device_id: str, session: SessionDep) -> MatterDeviceState:
    """Return the current attribute state for a Matter device from the server's cache."""
    from integrations.matter.server import MatterServerClient

    node_id = await _resolve_matter_node_id(device_id, session)
    try:
        async with MatterServerClient() as client:
            node = await client.get_node(node_id)
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not node:
        raise HTTPException(status_code=404, detail="Matter node not found on server")

    attrs: dict[str, Any] = node.get("attributes") or {}
    return MatterDeviceState(
        device_id=device_id,
        node_id=node_id,
        online=node.get("available", False),
        on_off=_read_cluster_attr(attrs, "6", "OnOff"),
        brightness=_read_cluster_attr(attrs, "8", "CurrentLevel"),
    )


# ── Shelly local control ──────────────────────────────────────────────────────


async def _run_shelly_switch(ip: str, command: str) -> tuple[bool, str]:
    """Execute a Shelly on/off command, returning (succeeded, event_type)."""
    from integrations.shelly_local.client import ShellyLocalController

    ctrl = ShellyLocalController(ip)
    try:
        if command == "turn_on":
            return await ctrl.turn_on(), "turned_on"
        if command == "turn_off":
            return await ctrl.turn_off(), "turned_off"
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    raise HTTPException(status_code=400, detail=f"Unknown command: {command}")


async def _require_device_and_ip(
    device_id: str, session: AsyncSession
) -> tuple[dict[str, Any], str]:
    """Load a device row and its stored IP address, or raise 404 / 422."""
    from devices.registry import get_device_by_id

    row = await get_device_by_id(device_id, session)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    ip = row.get("ip_address") or ""
    if not ip:
        raise HTTPException(status_code=422, detail="Device has no IP address stored")
    return row, ip


async def _shelly_live_state(
    device_id: str, ip: str, row: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    """Fetch a Shelly device's live state, recording a power reading or an offline event."""
    from devices.state_history import record_state_change
    from integrations.shelly_local.client import ShellyLocalController

    try:
        state = await ShellyLocalController(ip).get_state()
    except Exception as exc:
        await record_state_change(
            device_id=device_id,
            event_type="went_offline",
            session=session,
            property_id=row.get("property_id"),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    await record_state_change(
        device_id=device_id,
        event_type="power_reading",
        session=session,
        property_id=row.get("property_id"),
        value=str(state["power"]),
    )
    return {"device_id": device_id, "online": True, **state}


@router.post("/{device_id}/control", response_model=DeviceCommandResult)
async def control_device(
    device_id: str, payload: ControlPayload, settings: SettingsDep, session: SessionDep
) -> DeviceCommandResult:
    """Send turn_on / turn_off to a Shelly device using its saved IP address."""
    if settings.demo_mode:
        from demo.data import is_demo_device

        if is_demo_device(device_id):
            return DeviceCommandResult(success=True, state=payload.command == "turn_on")

    from devices.state_history import record_state_change

    row, ip = await _require_device_and_ip(device_id, session)
    ok, event_type = await _run_shelly_switch(ip, payload.command)
    if ok:
        await record_state_change(
            device_id=device_id,
            event_type=event_type,
            session=session,
            property_id=row.get("property_id"),
        )
    return DeviceCommandResult(success=ok, state=payload.command == "turn_on")


@router.get("/{device_id}/state")
async def device_state(
    device_id: str, settings: SettingsDep, session: SessionDep
) -> dict[str, Any]:
    """Return live on/off + power draw for a locally-reachable Shelly device.

    Shape differs between the demo and live paths (a known inconsistency), so the
    response stays untyped until the two are unified.
    """
    if settings.demo_mode:
        from demo.data import demo_device_state as _demo_state
        from demo.data import get_demo_device, is_demo_device

        if is_demo_device(device_id):
            d = get_demo_device(device_id)
            if not d:
                raise HTTPException(status_code=404, detail="Device not found")
            return _demo_state(d)

    row, ip = await _require_device_and_ip(device_id, session)
    return await _shelly_live_state(device_id, ip, row, session)


@router.get("/{device_id}/power-history")
async def device_power_history(
    device_id: str, settings: SettingsDep, session: SessionDep
) -> list[dict[str, Any]]:
    """Return power readings for the last 24 hours for charting."""
    if settings.demo_mode:
        from demo.data import is_demo_device

        if is_demo_device(device_id):
            from demo.history import get_demo_power_history

            return get_demo_power_history(device_id)
    from devices.state_history import get_power_history

    return await get_power_history(device_id, session)


@router.get("/{device_id}/history")
async def device_history(
    device_id: str, settings: SettingsDep, session: SessionDep
) -> list[dict[str, Any]]:
    """Return the last 50 state change events for a device, newest first."""
    if settings.demo_mode:
        from demo.data import is_demo_device

        if is_demo_device(device_id):
            from demo.history import get_demo_history

            return get_demo_history(device_id, limit=50)
    from devices.state_history import get_device_history

    return await get_device_history(device_id, session, limit=50)


# ── Room assignment ───────────────────────────────────────────────────────────


@router.patch("/{device_id}")
async def assign_device_room(
    device_id: str, payload: AssignRoomPayload, session: SessionDep
) -> dict[str, Any]:
    """Update a device's room assignment. Validates the room belongs to the same property."""
    from devices.registry import assign_device_room as _assign
    from devices.registry import get_device_by_id
    from properties.room_service import get_room_by_id

    device_row = await get_device_by_id(device_id, session)
    if not device_row:
        raise HTTPException(status_code=404, detail="Device not found")

    if payload.room_id is not None:
        room_row = await get_room_by_id(payload.room_id, session)
        if not room_row:
            raise HTTPException(status_code=404, detail="Room not found")
        if room_row.get("property_id") != device_row.get("property_id"):
            raise HTTPException(
                status_code=422,
                detail="Cannot move device to a room in a different property",
            )

    return await _assign(device_id, payload.room_id, session)


# ── Delete device ─────────────────────────────────────────────────────────────


@router.delete("/{device_id}", response_model=DeleteResult)
async def delete_device_endpoint(device_id: str, session: SessionDep) -> DeleteResult:
    """Delete a device and its state history from the registry."""
    from devices.registry import delete_device, get_device_by_id
    from devices.state_history import delete_device_history

    row = await get_device_by_id(device_id, session)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")

    try:
        await delete_device_history(device_id, session)
    except Exception as exc:
        logger.warning("Could not delete state history for %s: %s", device_id, exc)

    await delete_device(device_id, session)
    return DeleteResult(deleted=device_id)


# ── Generic device lookup ─────────────────────────────────────────────────────


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, settings: SettingsDep, session: SessionDep) -> dict[str, Any]:
    """Return current state for a single device by its Alphacon ID."""
    device = await device_service.get_device(device_id, settings, session)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device.to_api()
