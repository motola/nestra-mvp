"""Portfolio and Property management API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from db import SessionLocal, org_scope
from identity.repository.models import PortfolioModel
from property.repository.models import PropertyModel

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


class PortfolioCreateRequest(BaseModel):
    """Request to create a portfolio."""

    organization_id: UUID
    name: str
    description: str = ""


class PortfolioResponse(BaseModel):
    """Portfolio response."""

    id: UUID
    name: str
    description: str
    organization_id: UUID
    is_default: bool
    created_at: datetime


class PropertyCreateRequest(BaseModel):
    """Request to create a property."""

    organization_id: UUID
    portfolio_id: UUID
    name: str
    address: str
    property_type: str
    units: int = 1
    timezone: str = "UTC"
    description: str = ""


class PropertyResponse(BaseModel):
    """Property response."""

    id: UUID
    portfolio_id: UUID
    organization_id: UUID
    name: str
    address: str
    property_type: str
    units: int
    timezone: str
    description: str | None
    created_at: datetime


@router.get("", response_model=list[PortfolioResponse])
async def list_portfolios(organization_id: UUID) -> list[PortfolioResponse]:
    """List all portfolios for an organization."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        stmt = select(PortfolioModel).where(PortfolioModel.organization_id == organization_id)
        result = await db.execute(stmt)
        portfolios = result.scalars().all()

        return [
            PortfolioResponse(
                id=portfolio.id,
                name=portfolio.name,
                description=portfolio.description,
                organization_id=portfolio.organization_id,
                is_default=portfolio.is_default,
                created_at=portfolio.created_at,
            )
            for portfolio in portfolios
        ]


@router.post("", response_model=PortfolioResponse)
async def create_portfolio(request: PortfolioCreateRequest) -> PortfolioResponse:
    """Create a new portfolio."""
    async with SessionLocal() as db, org_scope(db, request.organization_id):
        now = datetime.now(UTC)

        portfolio = PortfolioModel(
            organization_id=request.organization_id,
            name=request.name,
            description=request.description,
            is_default=False,
            created_at=now,
        )

        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            organization_id=portfolio.organization_id,
            is_default=portfolio.is_default,
            created_at=portfolio.created_at,
        )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: UUID) -> PortfolioResponse:
    """Get a portfolio by ID."""
    async with SessionLocal() as db:
        stmt = select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        result = await db.execute(stmt)
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Validate org scope BEFORE returning any portfolio data
        async with org_scope(db, portfolio.organization_id):
            # Query within org scope to ensure access validation
            return PortfolioResponse(
                id=portfolio.id,
                name=portfolio.name,
                description=portfolio.description,
                organization_id=portfolio.organization_id,
                is_default=portfolio.is_default,
                created_at=portfolio.created_at,
            )


@router.post("/{portfolio_id}/properties", response_model=PropertyResponse)
async def create_property(portfolio_id: UUID, request: PropertyCreateRequest) -> PropertyResponse:
    """Create a new property in a portfolio."""
    if request.portfolio_id != portfolio_id:
        raise HTTPException(status_code=400, detail="Portfolio ID mismatch")

    async with SessionLocal() as db, org_scope(db, request.organization_id):
        # Verify portfolio exists
        stmt = select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        result = await db.execute(stmt)
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        now = datetime.now(UTC)

        property_obj = PropertyModel(
            portfolio_id=portfolio_id,
            organization_id=request.organization_id,
            name=request.name,
            address=request.address,
            property_type=request.property_type,
            units=request.units,
            timezone=request.timezone,
            description=request.description if request.description else None,
            created_at=now,
            updated_at=now,
        )

        db.add(property_obj)
        await db.commit()
        await db.refresh(property_obj)

        return PropertyResponse(
            id=property_obj.id,
            portfolio_id=property_obj.portfolio_id,
            organization_id=property_obj.organization_id,
            name=property_obj.name,
            address=property_obj.address,
            property_type=property_obj.property_type,
            units=property_obj.units,
            timezone=property_obj.timezone,
            description=property_obj.description,
            created_at=property_obj.created_at,
        )


@router.get("/{portfolio_id}/properties", response_model=list[PropertyResponse])
async def list_properties(portfolio_id: UUID, organization_id: UUID) -> list[PropertyResponse]:
    """List all properties in a portfolio."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        stmt = select(PropertyModel).where(PropertyModel.portfolio_id == portfolio_id)
        result = await db.execute(stmt)
        properties = result.scalars().all()

        return [
            PropertyResponse(
                id=prop.id,
                organization_id=prop.organization_id,
                portfolio_id=prop.portfolio_id,
                name=prop.name,
                address=prop.address,
                property_type=prop.property_type,
                units=prop.units,
                timezone=prop.timezone,
                description=prop.description,
                created_at=prop.created_at,
            )
            for prop in properties
        ]


class PortfolioUpdateRequest(BaseModel):
    """Request to update a portfolio."""

    name: str
    description: str = ""


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: UUID, request: PortfolioUpdateRequest, organization_id: UUID
) -> PortfolioResponse:
    """Update a portfolio."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        stmt = select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        result = await db.execute(stmt)
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        portfolio.name = request.name
        portfolio.description = request.description

        await db.commit()
        await db.refresh(portfolio)

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            organization_id=portfolio.organization_id,
            is_default=portfolio.is_default,
            created_at=portfolio.created_at,
        )


class PropertyUpdateRequest(BaseModel):
    """Request to update a property."""

    name: str
    address: str
    property_type: str
    units: int = 1
    timezone: str = "UTC"
    description: str = ""


@router.put("/{portfolio_id}/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    portfolio_id: UUID,
    property_id: UUID,
    request: PropertyUpdateRequest,
    organization_id: UUID,
) -> PropertyResponse:
    """Update a property."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        stmt = select(PropertyModel).where(PropertyModel.id == property_id)
        result = await db.execute(stmt)
        prop = result.scalar_one_or_none()

        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        if prop.portfolio_id != portfolio_id:
            raise HTTPException(
                status_code=400, detail="Property does not belong to this portfolio"
            )

        prop.name = request.name
        prop.address = request.address
        prop.property_type = request.property_type
        prop.units = request.units
        prop.timezone = request.timezone
        prop.description = request.description if request.description else None
        prop.updated_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(prop)

        return PropertyResponse(
            id=prop.id,
            organization_id=prop.organization_id,
            portfolio_id=prop.portfolio_id,
            name=prop.name,
            address=prop.address,
            property_type=prop.property_type,
            units=prop.units,
            timezone=prop.timezone,
            description=prop.description,
            created_at=prop.created_at,
        )
