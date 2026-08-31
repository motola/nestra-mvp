"""Integration management API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from db import SessionLocal
from identity.repository.models import OrganizationModel
from integrations.models import IntegrationModel
from integrations.provider import get_provider
from integrations.schemas import IntegrationCreateRequest, IntegrationResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    organization_id: UUID = Query(...),  # noqa: B008
) -> list[IntegrationResponse]:
    """List all integrations for an organization."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(IntegrationModel).where(
                IntegrationModel.organization_id == organization_id,
                IntegrationModel.deleted_at.is_(None),
            )
        )
        integrations = result.scalars().all()

        return [
            IntegrationResponse(
                id=integration.id,
                organization_id=integration.organization_id,
                provider_id=integration.provider_id,
                account_identifier=integration.account_identifier,
                connection_identifier=integration.connection_identifier,
                display_name=integration.display_name,
                enabled=integration.enabled,
                created_at=integration.created_at,
                updated_at=integration.updated_at,
            )
            for integration in integrations
        ]


@router.post("", response_model=IntegrationResponse)
async def create_integration(request: IntegrationCreateRequest) -> IntegrationResponse:
    """Create a new integration for an organization."""
    # Validate provider exists
    provider = get_provider(request.provider_id)
    if not provider:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: {request.provider_id}",
        )

    async with SessionLocal() as db:
        # Validate organization exists
        org_result = await db.execute(
            select(OrganizationModel).where(OrganizationModel.id == request.organization_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Check for duplicate integration
        dup_result = await db.execute(
            select(IntegrationModel).where(
                IntegrationModel.organization_id == request.organization_id,
                IntegrationModel.provider_id == request.provider_id,
                (IntegrationModel.connection_identifier == request.connection_identifier),
                IntegrationModel.deleted_at.is_(None),
            )
        )
        existing = dup_result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Integration already exists for {request.provider_id}",
            )

        now = datetime.now(UTC)

        # Create integration
        integration = IntegrationModel(
            organization_id=request.organization_id,
            provider_id=request.provider_id,
            connection_identifier=request.connection_identifier,
            display_name=request.display_name or provider.name,
            account_identifier=request.account_identifier,
            enabled=True,
            config=request.config,
            created_at=now,
            updated_at=now,
        )

        db.add(integration)
        await db.flush()

        if not integration.id:
            raise HTTPException(status_code=500, detail="Failed to create integration")

        await db.commit()

        return IntegrationResponse(
            id=integration.id,
            organization_id=integration.organization_id,
            provider_id=integration.provider_id,
            account_identifier=integration.account_identifier,
            connection_identifier=integration.connection_identifier,
            display_name=integration.display_name,
            enabled=integration.enabled,
            created_at=integration.created_at,
            updated_at=integration.updated_at,
        )
