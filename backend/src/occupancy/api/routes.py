"""Occupancy management API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from db import SessionLocal, org_scope
from occupancy.api.schemas import (
    RoomCreate,
    RoomList,
    RoomRead,
    RoomUpdate,
    StayCreate,
    StayList,
    StayRead,
    StayUpdate,
    TenantCreate,
    TenantList,
    TenantRead,
    TenantUpdate,
)
from occupancy.domain import Room, Stay, Tenant, TenantType
from occupancy.persistence.room_repository import RoomRepository
from occupancy.persistence.stay_repository import StayRepository
from occupancy.persistence.tenant_repository import TenantRepository
from occupancy.repository.models import RoomModel, StayModel, TenantModel

router = APIRouter(tags=["occupancy"])


# ============================================================================
# Tenant Routes
# ============================================================================


@router.get("/tenants", response_model=TenantList)
async def list_tenants(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> TenantList:
    """List all tenants for an organization."""
    if skip < 0 or limit < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination parameters")

    async with SessionLocal() as db, org_scope(db, organization_id):
        # Count total
        result = await db.execute(
            select(TenantModel).where(
                TenantModel.organization_id == organization_id,
                TenantModel.deleted_at.is_(None),
            )
        )
        total = len(result.scalars().all())

        # Get paginated items
        stmt = (
            select(TenantModel)
            .where(
                TenantModel.organization_id == organization_id,
                TenantModel.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        models = result.scalars().all()

        items = [
            TenantRead(
                id=model.id,
                organization_id=model.organization_id,
                user_id=model.user_id,
                full_name=model.full_name,
                email=model.email,
                phone=model.phone,
                tenant_type=model.tenant_type.value,
                created_at=model.created_at,
                updated_at=model.updated_at,
                deleted_at=model.deleted_at,
            )
            for model in models
        ]

        return TenantList(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )


@router.post("/tenants", response_model=TenantRead)
async def create_tenant(
    request: TenantCreate,
    organization_id: UUID,
) -> TenantRead:
    """Create a new tenant."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        tenant_repository = TenantRepository(db)

        tenant = Tenant(
            id=None,
            organization_id=organization_id,
            user_id=request.user_id,
            full_name=request.full_name,
            email=request.email,
            phone=request.phone,
            tenant_type=TenantType(request.tenant_type),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        created = await tenant_repository.create(tenant)
        await db.commit()

        return TenantRead(
            id=created.id,
            organization_id=created.organization_id,
            user_id=created.user_id,
            full_name=created.full_name,
            email=created.email,
            phone=created.phone,
            tenant_type=created.tenant_type,
            created_at=created.created_at,
            updated_at=created.updated_at,
            deleted_at=created.deleted_at,
        )


@router.get("/tenants/{tenant_id}", response_model=TenantRead)
async def get_tenant(tenant_id: UUID, organization_id: UUID) -> TenantRead:
    """Get a specific tenant."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        tenant_repository = TenantRepository(db)

        tenant = await tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        if tenant.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this tenant")

        return TenantRead(
            id=tenant.id,
            organization_id=tenant.organization_id,
            user_id=tenant.user_id,
            full_name=tenant.full_name,
            email=tenant.email,
            phone=tenant.phone,
            tenant_type=tenant.tenant_type,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
            deleted_at=tenant.deleted_at,
        )


@router.put("/tenants/{tenant_id}", response_model=TenantRead)
async def update_tenant(
    tenant_id: UUID,
    request: TenantUpdate,
    organization_id: UUID,
) -> TenantRead:
    """Update a tenant."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        tenant_repository = TenantRepository(db)

        tenant = await tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        if tenant.organization_id != organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this tenant")

        # Update only provided fields
        if request.full_name is not None:
            tenant.full_name = request.full_name
        if request.email is not None:
            tenant.email = request.email
        if request.phone is not None:
            tenant.phone = request.phone
        if request.tenant_type is not None:
            tenant.tenant_type = TenantType(request.tenant_type)

        updated = await tenant_repository.update(tenant)
        await db.commit()

        return TenantRead(
            id=updated.id,
            organization_id=updated.organization_id,
            user_id=updated.user_id,
            full_name=updated.full_name,
            email=updated.email,
            phone=updated.phone,
            tenant_type=updated.tenant_type,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            deleted_at=updated.deleted_at,
        )


# ============================================================================
# Room Routes
# ============================================================================


@router.get("/properties/{property_id}/rooms", response_model=RoomList)
async def list_rooms(
    property_id: UUID,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> RoomList:
    """List all rooms in a property."""
    if skip < 0 or limit < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination parameters")

    async with SessionLocal() as db, org_scope(db, organization_id):
        # Count total
        result = await db.execute(select(RoomModel).where(RoomModel.property_id == property_id))
        total = len(result.scalars().all())

        # Get paginated items
        stmt = (
            select(RoomModel).where(RoomModel.property_id == property_id).offset(skip).limit(limit)
        )
        result = await db.execute(stmt)
        models = result.scalars().all()

        items = [
            RoomRead(
                id=model.id,
                property_id=model.property_id,
                name=model.name,
                room_type=model.room_type,
                floor_number=model.floor_number,
                square_feet=model.square_feet,
                description=model.description,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]

        return RoomList(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )


@router.post("/properties/{property_id}/rooms", response_model=RoomRead)
async def create_room(
    property_id: UUID,
    request: RoomCreate,
    organization_id: UUID,
) -> RoomRead:
    """Create a new room in a property."""
    if request.property_id != property_id:
        raise HTTPException(status_code=400, detail="Property ID mismatch")

    async with SessionLocal() as db, org_scope(db, organization_id):
        room_repository = RoomRepository(db)

        room = Room(
            id=None,
            property_id=property_id,
            name=request.name,
            room_type=request.room_type,
            floor_number=request.floor_number,
            square_feet=request.square_feet,
            description=request.description,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        created = await room_repository.create(room)
        await db.commit()

        return RoomRead(
            id=created.id,
            property_id=created.property_id,
            name=created.name,
            room_type=created.room_type,
            floor_number=created.floor_number,
            square_feet=created.square_feet,
            description=created.description,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )


@router.get("/rooms/{room_id}", response_model=RoomRead)
async def get_room(room_id: UUID, organization_id: UUID) -> RoomRead:
    """Get a specific room."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        room_repository = RoomRepository(db)

        room = await room_repository.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        return RoomRead(
            id=room.id,
            property_id=room.property_id,
            name=room.name,
            room_type=room.room_type,
            floor_number=room.floor_number,
            square_feet=room.square_feet,
            description=room.description,
            created_at=room.created_at,
            updated_at=room.updated_at,
        )


@router.put("/rooms/{room_id}", response_model=RoomRead)
async def update_room(
    room_id: UUID,
    request: RoomUpdate,
    organization_id: UUID,
) -> RoomRead:
    """Update a room."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        room_repository = RoomRepository(db)

        room = await room_repository.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        # Update only provided fields
        if request.name is not None:
            room.name = request.name
        if request.room_type is not None:
            room.room_type = request.room_type
        if request.floor_number is not None:
            room.floor_number = request.floor_number
        if request.square_feet is not None:
            room.square_feet = request.square_feet
        if request.description is not None:
            room.description = request.description

        room.updated_at = datetime.now(UTC)
        updated = await room_repository.update(room)
        await db.commit()

        return RoomRead(
            id=updated.id,
            property_id=updated.property_id,
            name=updated.name,
            room_type=updated.room_type,
            floor_number=updated.floor_number,
            square_feet=updated.square_feet,
            description=updated.description,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )


# ============================================================================
# Stay Routes
# ============================================================================


@router.get("/properties/{property_id}/stays", response_model=StayList)
async def list_stays(
    property_id: UUID,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> StayList:
    """List all stays at a property."""
    if skip < 0 or limit < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination parameters")

    async with SessionLocal() as db, org_scope(db, organization_id):
        # Count total
        result = await db.execute(select(StayModel).where(StayModel.property_id == property_id))
        total = len(result.scalars().all())

        # Get paginated items
        stmt = (
            select(StayModel).where(StayModel.property_id == property_id).offset(skip).limit(limit)
        )
        result = await db.execute(stmt)
        models = result.scalars().all()

        items = [
            StayRead(
                id=model.id,
                property_id=model.property_id,
                check_in_date=model.check_in_date,
                check_out_date=model.check_out_date,
                status=model.status,
                notes=model.notes,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]

        return StayList(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )


@router.post("/properties/{property_id}/stays", response_model=StayRead)
async def create_stay(
    property_id: UUID,
    request: StayCreate,
    organization_id: UUID,
) -> StayRead:
    """Create a new stay at a property."""
    if request.property_id != property_id:
        raise HTTPException(status_code=400, detail="Property ID mismatch")

    async with SessionLocal() as db, org_scope(db, organization_id):
        stay_repository = StayRepository(db)

        stay = Stay(
            id=None,
            property_id=property_id,
            check_in_date=request.check_in_date,
            check_out_date=request.check_out_date,
            status=request.status,
            notes=request.notes,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        created = await stay_repository.create(stay)
        await db.commit()

        return StayRead(
            id=created.id,
            property_id=created.property_id,
            check_in_date=created.check_in_date,
            check_out_date=created.check_out_date,
            status=created.status,
            notes=created.notes,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )


@router.get("/stays/{stay_id}", response_model=StayRead)
async def get_stay(stay_id: UUID, organization_id: UUID) -> StayRead:
    """Get a specific stay."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        stay_repository = StayRepository(db)

        stay = await stay_repository.get_by_id(stay_id)
        if not stay:
            raise HTTPException(status_code=404, detail="Stay not found")

        return StayRead(
            id=stay.id,
            property_id=stay.property_id,
            check_in_date=stay.check_in_date,
            check_out_date=stay.check_out_date,
            status=stay.status,
            notes=stay.notes,
            created_at=stay.created_at,
            updated_at=stay.updated_at,
        )


@router.put("/stays/{stay_id}", response_model=StayRead)
async def update_stay(
    stay_id: UUID,
    request: StayUpdate,
    organization_id: UUID,
) -> StayRead:
    """Update a stay."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        stay_repository = StayRepository(db)

        stay = await stay_repository.get_by_id(stay_id)
        if not stay:
            raise HTTPException(status_code=404, detail="Stay not found")

        # Update only provided fields
        if request.check_in_date is not None:
            stay.check_in_date = request.check_in_date
        if request.check_out_date is not None:
            stay.check_out_date = request.check_out_date
        if request.status is not None:
            stay.status = request.status
        if request.notes is not None:
            stay.notes = request.notes

        stay.updated_at = datetime.now(UTC)
        updated = await stay_repository.update(stay)
        await db.commit()

        return StayRead(
            id=updated.id,
            property_id=updated.property_id,
            check_in_date=updated.check_in_date,
            check_out_date=updated.check_out_date,
            status=updated.status,
            notes=updated.notes,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
