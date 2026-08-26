"""WiFi scanning API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from core.dependencies import get_current_organization, get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from integrations.wifi.scanner import WiFiScanner
from property.domain import Device, DeviceType
from property.persistence.device_repository import DeviceRepository

router = APIRouter(prefix="/wifi", tags=["wifi"])


class WiFiNetworkResponse(BaseModel):
    """WiFi network response."""

    ssid: str
    bssid: str
    signal_strength: int
    channel: int
    security: str


class WiFiNetworkRequest(BaseModel):
    """WiFi network creation request."""

    ssid: str
    bssid: str
    signal_strength: int
    channel: int
    security: str


class WiFiDeviceCreationRequest(BaseModel):
    """Request to create devices from WiFi networks."""

    property_id: UUID
    networks: list[WiFiNetworkRequest]


class DeviceResponse(BaseModel):
    """Device response."""

    id: UUID
    vendor_name: str
    device_type: str
    online: bool


@router.post("/scan", response_model=list[WiFiNetworkResponse])
async def scan_wifi_networks() -> list[WiFiNetworkResponse]:
    """Scan for available WiFi networks.

    Returns a list of detected WiFi networks sorted by signal strength.
    Requires system-level permissions to scan networks.
    """
    try:
        networks = await WiFiScanner.scan()
        return [
            WiFiNetworkResponse(
                ssid=n.ssid,
                bssid=n.bssid,
                signal_strength=n.signal_strength,
                channel=n.channel,
                security=n.security,
            )
            for n in networks
        ]
    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail="WiFi scanning requires elevated permissions (admin/root)",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WiFi scanning failed: {str(e)}") from e


@router.post("/devices/create", response_model=list[DeviceResponse])
async def create_wifi_devices(
    request: WiFiDeviceCreationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    org_id: Annotated[UUID, Depends(get_current_organization)],
) -> list[DeviceResponse]:
    """Create devices from selected WiFi networks.

    Takes a list of WiFi networks and creates device entries for them.
    """
    repository = DeviceRepository(db)
    created_devices = []

    for network in request.networks:
        device = Device(
            id=None,
            organization_id=org_id,
            property_id=request.property_id,
            integration_id=None,
            vendor="wifi",
            vendor_specific_id=network.bssid,
            vendor_name=network.ssid,
            device_type=DeviceType.SENSOR,
            online=True,
            raw_state={
                "ssid": network.ssid,
                "bssid": network.bssid,
                "signal_strength": network.signal_strength,
                "channel": network.channel,
                "security": network.security,
            },
        )

        stored_device = await repository.upsert(device)
        created_devices.append(
            DeviceResponse(
                id=stored_device.id,
                vendor_name=stored_device.vendor_name,
                device_type=stored_device.device_type.value,
                online=stored_device.online,
            )
        )

    return created_devices
