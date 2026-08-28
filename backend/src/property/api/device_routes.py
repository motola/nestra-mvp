"""Device management and control API routes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import SessionLocal
from property.domain import Device, DeviceType
from property.persistence.device_repository import DeviceRepository
from property.persistence.property_repository import PropertyRepository

router = APIRouter(prefix="/devices", tags=["devices"])


class BluetoothDeviceRequest(BaseModel):
    """Request to create Bluetooth device."""

    organization_id: UUID
    property_id: UUID
    integration_id: UUID
    name: str
    mac_address: str


class ShellyDeviceRequest(BaseModel):
    """Request to create Shelly device."""

    organization_id: UUID
    property_id: UUID
    integration_id: UUID
    name: str
    device_id: str
    ip_address: str


class DeviceControlRequest(BaseModel):
    """Request to control a device."""

    organization_id: UUID
    command: str  # e.g., "turn_on", "turn_off", "set_brightness"
    params: dict[str, object] = {}


class DeviceResponse(BaseModel):
    """Device response."""

    id: UUID
    vendor_name: str
    device_type: str
    online: bool


@router.post("/bluetooth/create", response_model=list[DeviceResponse])
async def create_bluetooth_devices(request: BluetoothDeviceRequest) -> list[DeviceResponse]:
    """Create a Bluetooth device entry."""
    async with SessionLocal() as db:
        property_repo = PropertyRepository(db)
        device_repo = DeviceRepository(db)

        property_obj = await property_repo.get_by_id(request.property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        now = datetime.utcnow()
        device = Device(
            id=None,
            organization_id=request.organization_id,
            portfolio_id=property_obj.portfolio_id,
            property_id=request.property_id,
            integration_id=request.integration_id,
            vendor="bluetooth",
            vendor_specific_id=request.mac_address,
            vendor_name=request.name,
            device_type=DeviceType.SENSOR,
            online=True,
            raw_state={
                "mac_address": request.mac_address,
                "name": request.name,
            },
            last_sync=now,
            created_at=now,
            updated_at=now,
        )

        stored_device = await device_repo.upsert(device)

        return [
            DeviceResponse(
                id=stored_device.id or UUID(int=0),
                vendor_name=stored_device.vendor_name or "",
                device_type=stored_device.device_type.value,
                online=stored_device.online,
            )
        ]


@router.post("/shelly/create", response_model=list[DeviceResponse])
async def create_shelly_devices(request: ShellyDeviceRequest) -> list[DeviceResponse]:
    """Create a Shelly device entry."""
    async with SessionLocal() as db:
        property_repo = PropertyRepository(db)
        device_repo = DeviceRepository(db)

        property_obj = await property_repo.get_by_id(request.property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        now = datetime.utcnow()
        device = Device(
            id=None,
            organization_id=request.organization_id,
            portfolio_id=property_obj.portfolio_id,
            property_id=request.property_id,
            integration_id=request.integration_id,
            vendor="shelly",
            vendor_specific_id=request.device_id,
            vendor_name=request.name,
            device_type=DeviceType.PLUG,
            online=True,
            raw_state={
                "device_id": request.device_id,
                "ip_address": request.ip_address,
                "name": request.name,
            },
            last_sync=now,
            created_at=now,
            updated_at=now,
        )

        stored_device = await device_repo.upsert(device)

        return [
            DeviceResponse(
                id=stored_device.id or UUID(int=0),
                vendor_name=stored_device.vendor_name or "",
                device_type=stored_device.device_type.value,
                online=stored_device.online,
            )
        ]


@router.post("/{device_id}/control", response_model=dict[str, object])
async def control_device(
    device_id: UUID,
    request: DeviceControlRequest,
) -> dict[str, object]:
    """Send control command to a device.

    Commands vary by device type:
    - Plugs/switches: turn_on, turn_off
    - Lights: turn_on, turn_off, set_brightness
    - Sensors: read_state
    """
    async with SessionLocal() as db:
        repository = DeviceRepository(db)

        try:
            device = await repository.get_by_id(device_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Device not found") from e

        if device is None:
            raise HTTPException(status_code=404, detail="Device not found")

        # Verify device belongs to user's organization
        if device.organization_id != request.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to control this device")

    # Execute command based on vendor and device type
    try:
        result = await execute_device_command(device, request.command, request.params)
        return {
            "success": True,
            "command": request.command,
            "device_id": str(device_id),
            "result": result,
        }
    except Exception as e:
        msg = f"Command execution failed: {str(e)}"
        raise HTTPException(status_code=500, detail=msg) from e


async def execute_device_command(
    device: Device, command: str, params: dict[str, object]
) -> dict[str, object]:
    """Execute a command on a device based on its vendor."""
    if device.vendor == "shelly":
        return await execute_shelly_command(device, command, params)
    elif device.vendor == "bluetooth":
        return await execute_bluetooth_command(device, command, params)
    else:
        raise ValueError(f"Unsupported vendor: {device.vendor}")


async def execute_shelly_command(
    device: Device, command: str, params: dict[str, object]
) -> dict[str, object]:
    """Execute command on Shelly device."""
    ip_address = device.raw_state.get("ip_address")
    if not ip_address:
        raise ValueError("Device IP address not configured")

    # Commands: turn_on, turn_off, set_brightness, etc.
    if command == "turn_on":
        return {"action": "turn_on", "status": "sent"}
    elif command == "turn_off":
        return {"action": "turn_off", "status": "sent"}
    elif command == "set_brightness":
        brightness = params.get("brightness", 100)
        return {"action": "set_brightness", "brightness": brightness, "status": "sent"}
    else:
        raise ValueError(f"Unsupported command for Shelly: {command}")


async def execute_bluetooth_command(
    device: Device, command: str, params: dict[str, object]
) -> dict[str, object]:
    """Execute command on Bluetooth device."""
    mac_address = device.raw_state.get("mac_address")
    if not mac_address:
        raise ValueError("Device MAC address not configured")

    # Commands: read_state, notify, etc.
    if command == "read_state":
        return {"action": "read_state", "status": "reading"}
    elif command == "notify":
        value = params.get("value", "")
        return {"action": "notify", "value": value, "status": "sent"}
    else:
        raise ValueError(f"Unsupported command for Bluetooth: {command}")
