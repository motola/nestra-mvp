"""Bluetooth integration API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from dependencies import SettingsDep
from integrations.bluetooth.schemas import (
    BluetoothDeviceIn,
    BluetoothDeviceOut,
    BluetoothPairResponse,
    BluetoothUnpairResponse,
)

router = APIRouter(prefix="/integrations/bluetooth", tags=["property"])

# ─── Mock storage (replace with real DB when wired) ────────────────────────────

_MOCK_DEVICES: dict[UUID, BluetoothDeviceOut] = {}
_MOCK_INTEGRATIONS: dict[str, UUID] = {}  # vendor → integration_id


@router.post("/pair", response_model=BluetoothPairResponse, status_code=status.HTTP_201_CREATED)
async def pair_device(
    body: BluetoothDeviceIn,
    settings: SettingsDep,
) -> BluetoothPairResponse:
    """Pair a Bluetooth device to a property."""
    # Check if device already paired
    existing = next(
        (d for d in _MOCK_DEVICES.values() if d.mac_address == body.mac_address),
        None,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device already paired",
        )

    # Get or create Bluetooth integration
    integration_id = _MOCK_INTEGRATIONS.get("bluetooth", uuid4())
    if "bluetooth" not in _MOCK_INTEGRATIONS:
        _MOCK_INTEGRATIONS["bluetooth"] = integration_id

    # Create device
    device_id = uuid4()
    device = BluetoothDeviceOut(
        id=device_id,
        property_id=body.property_id,
        mac_address=body.mac_address,
        name=body.name,
        device_type=body.device_type,
        rssi=body.rssi,
        battery_level=body.battery_level,
        is_paired=True,
        last_sync=datetime.now(tz=UTC),
        created_at=datetime.now(tz=UTC),
    )
    _MOCK_DEVICES[device_id] = device

    return BluetoothPairResponse(device_id=device_id)


@router.post("/unpair", response_model=BluetoothUnpairResponse)
async def unpair_device(
    device_id: UUID,
    settings: SettingsDep,
) -> BluetoothUnpairResponse:
    """Unpair a Bluetooth device."""
    if device_id not in _MOCK_DEVICES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    del _MOCK_DEVICES[device_id]

    return BluetoothUnpairResponse()


@router.get("/devices", response_model=list[BluetoothDeviceOut])
async def list_devices(
    property_id: UUID | None = None,
    settings: SettingsDep | None = None,
) -> list[BluetoothDeviceOut]:
    """List Bluetooth devices (RLS will filter by org in production)."""
    devices = list(_MOCK_DEVICES.values())
    if property_id:
        devices = [d for d in devices if d.property_id == property_id]

    return devices
