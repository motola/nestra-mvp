"""Integration management API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import SessionLocal
from integrations.models import IntegrationModel
from integrations.provider import get_provider

router = APIRouter(prefix="/integrations", tags=["integrations"])


class IntegrationCreate(BaseModel):
    """Request to create an integration."""

    organization_id: UUID
    provider_id: str = Field(..., description="Provider ID (e.g., 'bluetooth', 'shelly')")
    connection_identifier: str | None = Field(
        None, description="Unique identifier for this connection (e.g., MAC address, account name)"
    )
    display_name: str | None = Field(None, description="Human-readable name for this integration")
    config: dict[str, object] = Field(
        default_factory=dict, description="Provider-specific configuration"
    )


class IntegrationResponse(BaseModel):
    """Integration response."""

    id: UUID
    organization_id: UUID
    provider_id: str
    connection_identifier: str | None
    display_name: str | None
    enabled: bool
    created_at: datetime


@router.post("", response_model=IntegrationResponse)
async def create_integration(request: IntegrationCreate) -> IntegrationResponse:
    """Create a new integration for an organization."""
    # Validate provider exists
    provider = get_provider(request.provider_id)
    if not provider:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: {request.provider_id}",
        )

    async with SessionLocal() as db:
        now = datetime.now(UTC)

        # Create integration
        integration = IntegrationModel(
            id=None,
            organization_id=request.organization_id,
            provider_id=request.provider_id,
            connection_identifier=request.connection_identifier,
            display_name=request.display_name or provider.name,
            account_identifier="",
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
            connection_identifier=integration.connection_identifier,
            display_name=integration.display_name,
            enabled=integration.enabled,
            created_at=integration.created_at,
        )
