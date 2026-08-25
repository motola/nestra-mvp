"""Device sync and control API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from integrations.registry import AdapterRegistry
from integrations.sync import DeviceSyncService
from property.persistence.device_repository import DeviceRepository

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncDevicesRequest(BaseModel):
    """Request to sync devices from a vendor."""

    credentials: dict[str, str] | None = None


class SyncDevicesResponse(BaseModel):
    """Response from device sync."""

    vendor: str
    synced: int
    devices: list[DeviceData]


class DeviceData(BaseModel):
    """Device response data."""

    id: str
    vendor: str
    vendor_name: str
    device_type: str
    online: bool
    raw_state: dict


class ExecuteCommandRequest(BaseModel):
    """Request to execute a command on a device."""

    command: str
    params: dict | None = None
    credentials: dict[str, str] | None = None


class ExecuteCommandResponse(BaseModel):
    """Response from executing a command."""

    success: bool
    message: str


@router.post("/properties/{property_id}/sync/{vendor}")
async def sync_devices(
    property_id: UUID,
    vendor: str,
    integration_id: UUID,
    request: SyncDevicesRequest,
    registry: AdapterRegistry,
    repository: DeviceRepository,
) -> SyncDevicesResponse:
    """Sync devices from a vendor for a property.

    Triggers device discovery via the vendor adapter and persists to DB.
    Accepts optional credentials for vendor API authentication.
    """
    try:
        service = DeviceSyncService(registry, repository)

        # Get current organization from property (would come from auth context)
        organization_id = UUID("00000000-0000-0000-0000-000000000001")

        devices = await service.sync_integration(
            vendor=vendor,
            organization_id=organization_id,
            property_id=property_id,
            integration_id=integration_id,
            credentials=request.credentials,
        )

        logger.info(f"Synced {len(devices)} devices for {vendor}")

        return SyncDevicesResponse(
            vendor=vendor,
            synced=len(devices),
            devices=[
                DeviceData(
                    id=str(d.id),
                    vendor=d.vendor,
                    vendor_name=d.vendor_name or vendor,
                    device_type=d.device_type,
                    online=d.online,
                    raw_state=d.raw_state,
                )
                for d in devices
            ],
        )
    except Exception as e:
        logger.error(f"Failed to sync devices from {vendor}: {e}")
        raise HTTPException(status_code=400, detail=f"Sync failed: {str(e)}") from e


@router.get("/properties/{property_id}/devices")
async def get_property_devices(
    property_id: UUID,
    repository: DeviceRepository,
) -> list[DeviceData]:
    """Get all devices for a property."""
    try:
        devices = await repository.find_by_property(property_id)

        return [
            DeviceData(
                id=str(d.id),
                vendor=d.vendor,
                vendor_name=d.vendor_name or d.vendor,
                device_type=d.device_type,
                online=d.online,
                raw_state=d.raw_state,
            )
            for d in devices
        ]
    except Exception as e:
        logger.error(f"Failed to fetch devices for property {property_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/devices/{device_id}")
async def get_device(
    device_id: UUID,
    repository: DeviceRepository,
) -> DeviceData:
    """Get a single device by ID."""
    try:
        device = await repository.find_by_id(device_id)

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        return DeviceData(
            id=str(device.id),
            vendor=device.vendor,
            vendor_name=device.vendor_name or device.vendor,
            device_type=device.device_type,
            online=device.online,
            raw_state=device.raw_state,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch device {device_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/devices/{device_id}/command")
async def execute_device_command(
    device_id: UUID,
    request: ExecuteCommandRequest,
    repository: DeviceRepository,
    registry: AdapterRegistry,
) -> ExecuteCommandResponse:
    """Execute a command on a device."""
    try:
        device = await repository.find_by_id(device_id)

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Get the adapter for this device's vendor
        adapter = registry.resolve(device.vendor)

        # Build kwargs for execute call
        exec_kwargs = {"command": request.command, "params": request.params or {}}
        if request.credentials:
            exec_kwargs.update(request.credentials)

        # Execute the command
        success = await adapter.execute(device, **exec_kwargs)

        # Refresh device state after command
        if success:
            state_kwargs = {}
            if request.credentials:
                state_kwargs.update(request.credentials)
            device = await adapter.fetch_state(device, **state_kwargs)
            await repository.upsert(device)

        return ExecuteCommandResponse(
            success=success,
            message="Command executed successfully" if success else "Command failed",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute command on device {device_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


class RefreshStateRequest(BaseModel):
    """Request to refresh device state."""

    credentials: dict[str, str] | None = None


@router.post("/devices/{device_id}/state")
async def refresh_device_state(
    device_id: UUID,
    request: RefreshStateRequest,
    repository: DeviceRepository,
    registry: AdapterRegistry,
) -> DeviceData:
    """Refresh device state from vendor API."""
    try:
        device = await repository.find_by_id(device_id)

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Get the adapter for this device's vendor
        adapter = registry.resolve(device.vendor)

        # Fetch fresh state from vendor
        state_kwargs = {}
        if request.credentials:
            state_kwargs.update(request.credentials)
        device = await adapter.fetch_state(device, **state_kwargs)

        # Save updated state
        device = await repository.upsert(device)

        return DeviceData(
            id=str(device.id),
            vendor=device.vendor,
            vendor_name=device.vendor_name or device.vendor,
            device_type=device.device_type,
            online=device.online,
            raw_state=device.raw_state,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh device state {device_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
