"""Capability discovery and management API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from db import SessionLocal
from property.api.schemas import CapabilityList, CapabilityRead, DeviceCapabilityRead
from property.capabilities.discovery import discover_device_capabilities
from property.domain import DeviceCapability
from property.persistence.capability_repository import (
    CapabilityRepository,
    DeviceCapabilityRepository,
)
from property.persistence.device_repository import DeviceRepository
from property.repository.models import CapabilityModel

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("", response_model=CapabilityList)
async def list_capabilities(
    skip: int = 0,
    limit: int = 100,
) -> CapabilityList:
    """List all capabilities (paginated)."""
    if skip < 0 or limit < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination parameters")

    async with SessionLocal() as db:
        # Count total
        result = await db.execute(select(CapabilityModel))
        total = len(result.scalars().all())

        # Get paginated items
        stmt = select(CapabilityModel).offset(skip).limit(limit)
        result = await db.execute(stmt)
        models = result.scalars().all()

        items = [
            CapabilityRead(
                id=model.id,
                code=model.code,
                name=model.name,
                description=model.description,
                category=model.category,
                created_at=model.created_at,
            )
            for model in models
        ]

        return CapabilityList(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )


@router.get("/{capability_id}", response_model=CapabilityRead)
async def get_capability(capability_id: UUID) -> CapabilityRead:
    """Get a single capability by ID."""
    async with SessionLocal() as db:
        capability_repository = CapabilityRepository(db)

        capability = await capability_repository.get_by_id(capability_id)
        if not capability:
            raise HTTPException(status_code=404, detail="Capability not found")

        return CapabilityRead(
            id=capability.id,
            code=capability.code,
            name=capability.name,
            description=capability.description,
            category=capability.category,
            created_at=capability.created_at,
        )


@router.post("/devices/{device_id}/discover", response_model=dict[str, object])
async def discover_device_capabilities_route(
    device_id: UUID,
    organization_id: UUID,
) -> dict[str, object]:
    """Discover and save device capabilities based on device type.

    Auto-detects capabilities based on device type (SENSOR → temperature, humidity readings,
    PLUG → on/off control, etc) and creates DeviceCapability records.
    """
    async with SessionLocal() as db:
        device_repository = DeviceRepository(db)
        capability_repository = CapabilityRepository(db)
        device_capability_repository = DeviceCapabilityRepository(db)

        # Get device
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Verify organization authorization
        if device.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this device")

        # Discover capabilities for device type
        discovered_capabilities = await discover_device_capabilities(device)

        if not discovered_capabilities:
            return {
                "device_id": str(device_id),
                "capabilities_discovered": 0,
                "message": "No capabilities discovered for device type",
            }

        # Create or fetch capability records and link to device
        created_links: list[DeviceCapabilityRead] = []

        for discovered_cap in discovered_capabilities:
            # Get or create capability
            existing_cap = await capability_repository.get_by_code(discovered_cap.code)

            if existing_cap:
                capability = existing_cap
            else:
                capability = await capability_repository.create(discovered_cap)

            # Create device capability link
            if capability.id is None:
                continue

            device_cap_domain = DeviceCapability(
                id=None,
                device_id=device_id,
                capability_id=capability.id,
                created_at=datetime.now(UTC),
            )
            device_cap = await device_capability_repository.create(device_cap_domain)

            created_links.append(
                DeviceCapabilityRead(
                    id=device_cap.id,
                    device_id=device_cap.device_id,
                    capability_id=device_cap.capability_id,
                    capability=CapabilityRead(
                        id=capability.id,
                        code=capability.code,
                        name=capability.name,
                        description=capability.description,
                        category=capability.category,
                        created_at=capability.created_at,
                    ),
                    created_at=device_cap.created_at,
                )
            )

        await db.commit()

        return {
            "device_id": str(device_id),
            "capabilities_discovered": len(created_links),
            "capabilities": [cap.model_dump() for cap in created_links],
        }


@router.get("/devices/{device_id}/capabilities", response_model=dict[str, object])
async def get_device_capabilities(
    device_id: UUID,
    organization_id: UUID,
) -> dict[str, object]:
    """Get all capabilities for a specific device."""
    async with SessionLocal() as db:
        device_repository = DeviceRepository(db)
        device_capability_repository = DeviceCapabilityRepository(db)

        # Get device and verify authorization
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        if device.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this device")

        # Get device capabilities
        device_capabilities = await device_capability_repository.list_by_device(device_id)

        return {
            "device_id": str(device_id),
            "capabilities": [
                {
                    "id": str(dc.id),
                    "device_id": str(dc.device_id),
                    "capability_id": str(dc.capability_id),
                    "created_at": dc.created_at.isoformat(),
                }
                for dc in device_capabilities
            ],
            "total": len(device_capabilities),
        }
