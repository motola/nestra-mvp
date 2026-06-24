"""Ecobee Thermostat API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from dependencies import SettingsDep
from integrations.ecobee.schemas import (
    EcobeeDeviceIn,
    EcobeeDeviceOut,
    EcobeeStatusResponse,
    EcobeeTemperatureUpdate,
)

router = APIRouter(prefix="/integrations/ecobee", tags=["property"])

_MOCK_DEVICES: dict[UUID, EcobeeDeviceOut] = {}
_MOCK_INTEGRATIONS: dict[str, UUID] = {}


@router.post("/thermostats", response_model=EcobeeDeviceOut, status_code=status.HTTP_201_CREATED)
async def add_thermostat(
    body: EcobeeDeviceIn,
    settings: SettingsDep,
) -> EcobeeDeviceOut:
    """Add an Ecobee Thermostat to a property."""
    existing = next(
        (device for device in _MOCK_DEVICES.values() if device.device_id == body.device_id),
        None,
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device already added")

    integration_id = _MOCK_INTEGRATIONS.get("ecobee", uuid4())
    if "ecobee" not in _MOCK_INTEGRATIONS:
        _MOCK_INTEGRATIONS["ecobee"] = integration_id

    device_id = uuid4()
    device = EcobeeDeviceOut(
        id=device_id,
        property_id=body.property_id,
        device_id=body.device_id,
        name=body.name,
        current_temperature=body.current_temperature,
        target_temperature=body.target_temperature,
        mode=body.mode,
        humidity=body.humidity,
        is_online=True,
        last_sync=datetime.now(tz=UTC),
        created_at=datetime.now(tz=UTC),
    )
    _MOCK_DEVICES[device_id] = device
    return device


@router.get("/thermostats", response_model=list[EcobeeDeviceOut])
async def list_thermostats(
    property_id: UUID | None = None,
    settings: SettingsDep | None = None,
) -> list[EcobeeDeviceOut]:
    """List Ecobee Thermostats."""
    devices = list(_MOCK_DEVICES.values())
    if property_id:
        devices = [device for device in devices if device.property_id == property_id]
    return devices


@router.post("/thermostats/{device_id}/temperature", response_model=EcobeeStatusResponse)
async def set_temperature(
    device_id: UUID,
    body: EcobeeTemperatureUpdate,
    settings: SettingsDep,
) -> EcobeeStatusResponse:
    """Update thermostat temperature."""
    if device_id not in _MOCK_DEVICES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    device = _MOCK_DEVICES[device_id]
    device.target_temperature = body.target_temperature
    device.last_sync = datetime.now(tz=UTC)
    _MOCK_DEVICES[device_id] = device

    return EcobeeStatusResponse(message=f"Temperature set to {body.target_temperature}°")


@router.delete("/thermostats/{device_id}", response_model=EcobeeStatusResponse)
async def remove_thermostat(
    device_id: UUID,
    settings: SettingsDep,
) -> EcobeeStatusResponse:
    """Remove a thermostat."""
    if device_id not in _MOCK_DEVICES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    device = _MOCK_DEVICES.pop(device_id)
    return EcobeeStatusResponse(message=f"Thermostat '{device.name}' removed")
