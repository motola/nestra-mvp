"""Device management and control API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import SessionLocal
from integrations.models import IntegrationModel
from integrations.provider import get_provider
from property.api.schemas import DeviceDetail
from property.audit.logger import AuditLogger
from property.domain import Device, DeviceIntegration, DevicePlacement, DeviceType
from property.persistence.capability_repository import DeviceCapabilityRepository
from property.persistence.device_integration_repository import DeviceIntegrationRepository
from property.persistence.device_placement_repository import DevicePlacementRepository
from property.persistence.device_repository import DeviceRepository
from property.persistence.property_repository import PropertyRepository

router = APIRouter(prefix="/integrations", tags=["devices"])


class BluetoothDeviceCreate(BaseModel):
    """Request to create Bluetooth device through integration."""

    property_id: UUID
    name: str
    mac_address: str
    room_id: UUID | None = None


class ShellyDeviceCreate(BaseModel):
    """Request to create Shelly device through integration."""

    property_id: UUID
    name: str
    device_id: str
    ip_address: str
    room_id: UUID | None = None


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


@router.post("/{integration_id}/devices/bluetooth", response_model=list[DeviceResponse])
async def create_bluetooth_device(
    integration_id: UUID, request: BluetoothDeviceCreate
) -> list[DeviceResponse]:
    """Create a Bluetooth device through an integration."""
    async with SessionLocal() as db:
        # Load integration and verify provider type
        integration = await db.get(IntegrationModel, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        provider = get_provider(integration.provider_id)
        if not provider or provider.slug != "bluetooth":
            raise HTTPException(
                status_code=400,
                detail=f"Integration is not a Bluetooth provider (got {integration.provider_id})",
            )

        property_repository = PropertyRepository(db)
        device_repository = DeviceRepository(db)
        placement_repository = DevicePlacementRepository(db)
        integration_repository = DeviceIntegrationRepository(db)
        audit_logger = AuditLogger(db)

        # Get property and verify it belongs to the integration's organization
        property_obj = await property_repository.get_by_id(request.property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        if property_obj.organization_id != integration.organization_id:
            raise HTTPException(
                status_code=403,
                detail="Property does not belong to integration's organization",
            )

        now = datetime.now(UTC)
        device = Device(
            id=None,
            organization_id=integration.organization_id,
            portfolio_id=property_obj.portfolio_id,
            property_id=request.property_id,
            integration_id=integration_id,
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

        stored_device = await device_repository.upsert(device)
        if not stored_device.id:
            raise HTTPException(status_code=500, detail="Failed to create device")

        # Log device creation
        await audit_logger.log_device_created(
            organization_id=integration.organization_id,
            device_id=stored_device.id,
            device_name=request.name,
        )

        # Create DevicePlacement (device location)
        placement = DevicePlacement(
            id=None,
            device_id=stored_device.id,
            property_id=request.property_id,
            room_id=request.room_id,
            created_at=now,
            updated_at=now,
        )
        await placement_repository.create(placement)

        # Create DeviceIntegration (connectivity link)
        device_integration = DeviceIntegration(
            id=None,
            device_id=stored_device.id,
            integration_id=integration_id,
            connection_identifier=request.mac_address,
            discovered_at=now,
            last_synced_at=now,
            created_at=now,
            updated_at=now,
        )
        await integration_repository.create(device_integration)

        await db.commit()

        return [
            DeviceResponse(
                id=stored_device.id,
                vendor_name=stored_device.vendor_name or "",
                device_type=stored_device.device_type.value,
                online=stored_device.online,
            )
        ]


@router.post("/{integration_id}/devices/shelly", response_model=list[DeviceResponse])
async def create_shelly_device(
    integration_id: UUID, request: ShellyDeviceCreate
) -> list[DeviceResponse]:
    """Create a Shelly device through an integration."""
    async with SessionLocal() as db:
        # Load integration and verify provider type
        integration = await db.get(IntegrationModel, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        provider = get_provider(integration.provider_id)
        if not provider or provider.slug != "shelly":
            raise HTTPException(
                status_code=400,
                detail=f"Integration is not a Shelly provider (got {integration.provider_id})",
            )

        property_repository = PropertyRepository(db)
        device_repository = DeviceRepository(db)
        placement_repository = DevicePlacementRepository(db)
        integration_repository = DeviceIntegrationRepository(db)
        audit_logger = AuditLogger(db)

        # Get property and verify it belongs to the integration's organization
        property_obj = await property_repository.get_by_id(request.property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        if property_obj.organization_id != integration.organization_id:
            raise HTTPException(
                status_code=403,
                detail="Property does not belong to integration's organization",
            )

        now = datetime.now(UTC)
        device = Device(
            id=None,
            organization_id=integration.organization_id,
            portfolio_id=property_obj.portfolio_id,
            property_id=request.property_id,
            integration_id=integration_id,
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

        stored_device = await device_repository.upsert(device)
        if not stored_device.id:
            raise HTTPException(status_code=500, detail="Failed to create device")

        # Log device creation
        await audit_logger.log_device_created(
            organization_id=integration.organization_id,
            device_id=stored_device.id,
            device_name=request.name,
        )

        # Create DevicePlacement (device location)
        placement = DevicePlacement(
            id=None,
            device_id=stored_device.id,
            property_id=request.property_id,
            room_id=request.room_id,
            created_at=now,
            updated_at=now,
        )
        await placement_repository.create(placement)

        # Create DeviceIntegration (connectivity link)
        device_integration = DeviceIntegration(
            id=None,
            device_id=stored_device.id,
            integration_id=integration_id,
            connection_identifier=request.device_id,
            discovered_at=now,
            last_synced_at=now,
            created_at=now,
            updated_at=now,
        )
        await integration_repository.create(device_integration)

        await db.commit()

        return [
            DeviceResponse(
                id=stored_device.id,
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


@router.get("/{device_id}", response_model=DeviceDetail)
async def get_device_detail(
    device_id: UUID,
    organization_id: UUID,
) -> DeviceDetail:
    """Get detailed device information including placement, integrations, and capabilities."""
    async with SessionLocal() as db:
        device_repository = DeviceRepository(db)
        placement_repository = DevicePlacementRepository(db)
        device_capability_repository = DeviceCapabilityRepository(db)

        # Get device
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Verify organization authorization
        if device.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this device")

        # Get placement info
        placement = await placement_repository.get_by_device_id(device_id)
        placement_data: dict[str, object] | None = None
        if placement:
            placement_data = {
                "placement_id": str(placement.id),
                "device_id": str(placement.device_id),
                "property_id": str(placement.property_id),
                "room_id": str(placement.room_id) if placement.room_id else None,
                "placement_type": placement.placement_type,
                "created_at": placement.created_at.isoformat(),
                "updated_at": placement.updated_at.isoformat(),
            }

        # Get device capabilities
        device_capabilities = await device_capability_repository.list_by_device(device_id)
        capabilities_list = []
        for dc in device_capabilities:
            cap_dict = {
                "id": str(dc.id),
                "device_id": str(dc.device_id),
                "capability_id": str(dc.capability_id),
                "created_at": dc.created_at.isoformat(),
            }
            capabilities_list.append(cap_dict)

        return DeviceDetail(
            id=device.id,
            organization_id=device.organization_id,
            portfolio_id=device.portfolio_id,
            property_id=device.property_id,
            integration_id=device.integration_id,
            device_type=device.device_type.value,
            vendor=device.vendor,
            vendor_specific_id=device.vendor_specific_id,
            vendor_name=device.vendor_name,
            online=device.online,
            last_sync=device.last_sync,
            category=device.category,
            manufacturer=device.manufacturer,
            model=device.model,
            serial_number=device.serial_number,
            placement=placement_data,
            capabilities=capabilities_list,  # type: ignore
            created_at=device.created_at,
            updated_at=device.updated_at,
        )
