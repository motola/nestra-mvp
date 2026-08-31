"""Access control and audit logging API routes."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from db import SessionLocal
from property.access.checker import AccessChecker
from property.api.access_schemas import (
    AuditEventList,
    AuditEventRead,
    AuditEventSummary,
    DeviceAccessGrantCreate,
    DeviceAccessGrantList,
    DeviceAccessGrantRead,
    DeviceAccessGrantUpdate,
    MagicLinkTokenClaimResponse,
    MagicLinkTokenCreate,
    MagicLinkTokenRead,
    MagicLinkTokenWithToken,
)
from property.audit.logger import AuditLogger
from property.domain.access import AccessType, DeviceAccessGrant
from property.domain.tokens import MagicLinkToken
from property.persistence.audit_event_repository import AuditEventRepository
from property.persistence.device_access_grant_repository import DeviceAccessGrantRepository
from property.persistence.magic_link_token_repository import MagicLinkTokenRepository

router = APIRouter(prefix="/access", tags=["access"])


# Device Access Grants Endpoints


@router.post("/devices/{device_id}/access-grants", response_model=DeviceAccessGrantRead)
async def create_device_access_grant(
    device_id: UUID,
    request_body: DeviceAccessGrantCreate,
    request: Request,
) -> DeviceAccessGrantRead:
    """Grant access to a device for a user."""
    if not request_body.grantee_user_id and not request_body.grantee_email:
        raise HTTPException(
            status_code=400, detail="Either grantee_user_id or grantee_email must be provided"
        )

    async with SessionLocal() as db:
        grant_repo = DeviceAccessGrantRepository(db)
        audit_logger = AuditLogger(db)

        grant = DeviceAccessGrant(
            id=None,
            organization_id=device_id,  # TODO: Get from request context
            device_id=device_id,
            grantee_user_id=request_body.grantee_user_id,
            grantee_email=request_body.grantee_email,
            granted_by_user_id=device_id,  # TODO: Get from auth context
            access_type=AccessType(request_body.access_type),
            capabilities=request_body.capabilities,
            expires_at=request_body.expires_at,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            revoked_at=None,
        )

        created_grant = await grant_repo.create(grant)

        # Log the access grant creation
        await audit_logger.log_access_granted(
            organization_id=grant.organization_id,
            grant_id=created_grant.id or device_id,
            grantee_user_id=request_body.grantee_user_id,
            grantee_email=request_body.grantee_email,
            device_id=device_id,
            ip_address=request.client.host if request.client else None,
        )

        await db.commit()

        return DeviceAccessGrantRead(
            id=created_grant.id or device_id,
            device_id=created_grant.device_id,
            grantee_user_id=created_grant.grantee_user_id,
            grantee_email=created_grant.grantee_email,
            access_type=created_grant.access_type,
            capabilities=created_grant.capabilities,
            expires_at=created_grant.expires_at,
            created_at=created_grant.created_at,
            updated_at=created_grant.updated_at,
            revoked_at=created_grant.revoked_at,
        )


@router.get("/devices/{device_id}/access-grants", response_model=DeviceAccessGrantList)
async def list_device_access_grants(
    device_id: UUID, skip: int = 0, limit: int = 100
) -> DeviceAccessGrantList:
    """List who has access to a device."""
    async with SessionLocal() as db:
        grant_repo = DeviceAccessGrantRepository(db)
        grants = await grant_repo.list_by_device(device_id, skip, limit)

        return DeviceAccessGrantList(
            items=[
                DeviceAccessGrantRead(
                    id=g.id or device_id,
                    device_id=g.device_id,
                    grantee_user_id=g.grantee_user_id,
                    grantee_email=g.grantee_email,
                    access_type=g.access_type,
                    capabilities=g.capabilities,
                    expires_at=g.expires_at,
                    created_at=g.created_at,
                    updated_at=g.updated_at,
                    revoked_at=g.revoked_at,
                )
                for g in grants
            ],
            total=len(grants),
            skip=skip,
            limit=limit,
        )


@router.put("/access-grants/{grant_id}", response_model=DeviceAccessGrantRead)
async def update_access_grant(
    grant_id: UUID, request_body: DeviceAccessGrantUpdate, request: Request
) -> DeviceAccessGrantRead:
    """Update an access grant (extend expiry, change capabilities)."""
    async with SessionLocal() as db:
        grant_repo = DeviceAccessGrantRepository(db)
        grant = await grant_repo.get_by_id(grant_id)

        if not grant:
            raise HTTPException(status_code=404, detail="Access grant not found")

        # Update fields
        if request_body.access_type:
            grant.access_type = AccessType(request_body.access_type)
        if request_body.capabilities is not None:
            grant.capabilities = request_body.capabilities
        if request_body.expires_at is not None:
            grant.expires_at = request_body.expires_at

        grant.updated_at = datetime.now(UTC)

        # Manually update the model since we don't have a direct update method
        from sqlalchemy import select

        from property.repository.models import DeviceAccessGrantModel

        stmt = select(DeviceAccessGrantModel).where(DeviceAccessGrantModel.id == grant_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.access_type = AccessType(grant.access_type)
            model.capabilities = grant.capabilities
            model.expires_at = grant.expires_at
            model.updated_at = grant.updated_at
            await db.flush()

        await db.commit()

        return DeviceAccessGrantRead(
            id=grant.id or grant_id,
            device_id=grant.device_id,
            grantee_user_id=grant.grantee_user_id,
            grantee_email=grant.grantee_email,
            access_type=grant.access_type,
            capabilities=grant.capabilities,
            expires_at=grant.expires_at,
            created_at=grant.created_at,
            updated_at=grant.updated_at,
            revoked_at=grant.revoked_at,
        )


@router.delete("/access-grants/{grant_id}")
async def revoke_access_grant(grant_id: UUID, request: Request) -> dict[str, str]:
    """Revoke access to a device."""
    async with SessionLocal() as db:
        grant_repo = DeviceAccessGrantRepository(db)
        grant = await grant_repo.get_by_id(grant_id)

        if not grant:
            raise HTTPException(status_code=404, detail="Access grant not found")

        audit_logger = AuditLogger(db)
        await grant_repo.revoke(grant_id)

        # Log the revocation
        await audit_logger.log_access_revoked(
            organization_id=grant.organization_id,
            grant_id=grant_id,
            grantee_user_id=grant.grantee_user_id,
            grantee_email=grant.grantee_email,
            ip_address=request.client.host if request.client else None,
        )

        await db.commit()

        return {"status": "success", "message": "Access grant revoked"}


@router.get("/my-devices")
async def list_my_devices(user_id: UUID) -> list[dict[str, object]]:
    """List all devices the user can access."""
    async with SessionLocal() as db:
        checker = AccessChecker(db)
        device_ids = await checker.get_user_accessible_devices(user_id)

        # TODO: Fetch device details from device repository
        return [{"device_id": str(device_id)} for device_id in device_ids]


# Magic Link Token Endpoints


@router.post("/devices/{device_id}/share-links", response_model=MagicLinkTokenWithToken)
async def create_share_link(
    device_id: UUID, request_body: MagicLinkTokenCreate, request: Request
) -> MagicLinkTokenWithToken:
    """Create a magic link for sharing device access."""
    async with SessionLocal() as db:
        token_repo = MagicLinkTokenRepository(db)
        audit_logger = AuditLogger(db)

        # Generate token
        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(hours=request_body.expires_in_hours)

        magic_token = MagicLinkToken(
            id=None,
            organization_id=device_id,  # TODO: Get from context
            device_id=device_id,
            access_type=request_body.access_type,
            token=token_value,
            created_by_user_id=device_id,  # TODO: Get from auth
            claimed_by_user_id=None,
            claimed_at=None,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
            revoked_at=None,
        )

        created_token = await token_repo.create(magic_token)

        # Log share link creation
        await audit_logger.log_share_link_created(
            organization_id=magic_token.organization_id,
            token_id=created_token.id or device_id,
            device_id=device_id,
            ip_address=request.client.host if request.client else None,
        )

        await db.commit()

        return MagicLinkTokenWithToken(
            id=created_token.id or device_id,
            token=token_value,
            device_id=created_token.device_id,
            access_type=created_token.access_type,
            created_at=created_token.created_at,
            expires_at=created_token.expires_at,
            share_link=f"/share/{token_value}",  # TODO: Use actual base URL
        )


@router.get("/devices/{device_id}/share-links", response_model=list[MagicLinkTokenRead])
async def list_share_links(
    device_id: UUID, skip: int = 0, limit: int = 100
) -> list[MagicLinkTokenRead]:
    """List active share links for a device."""
    async with SessionLocal() as db:
        token_repo = MagicLinkTokenRepository(db)
        tokens = await token_repo.list_by_device(device_id, skip, limit)

        return [
            MagicLinkTokenRead(
                id=t.id or UUID(int=0),
                device_id=t.device_id,
                access_type=t.access_type,
                created_at=t.created_at,
                claimed_at=t.claimed_at,
                expires_at=t.expires_at,
                revoked_at=t.revoked_at,
            )
            for t in tokens
        ]


@router.post("/share-links/{token}/claim", response_model=MagicLinkTokenClaimResponse)
async def claim_share_link(
    token: str, user_id: UUID, request: Request
) -> MagicLinkTokenClaimResponse:
    """User claims a shared access link."""
    async with SessionLocal() as db:
        token_repo = MagicLinkTokenRepository(db)
        magic_token = await token_repo.get_by_token(token)

        if not magic_token:
            raise HTTPException(status_code=404, detail="Share link not found")

        success = await token_repo.claim_token(token, user_id)

        if not success:
            raise HTTPException(status_code=400, detail="Share link expired or already claimed")

        audit_logger = AuditLogger(db)
        await audit_logger.log_share_link_claimed(
            organization_id=magic_token.organization_id,
            token_id=magic_token.id or UUID(int=0),
            claimed_by_user_id=user_id,
            ip_address=request.client.host if request.client else None,
        )

        await db.commit()

        return MagicLinkTokenClaimResponse(
            success=True,
            message="Share link claimed successfully",
            device_id=magic_token.device_id,
        )


@router.delete("/share-links/{token_id}")
async def revoke_share_link(token_id: UUID, request: Request) -> dict[str, str]:
    """Revoke a magic link token."""
    async with SessionLocal() as db:
        token_repo = MagicLinkTokenRepository(db)
        magic_token = await token_repo.get_by_id(token_id)

        if not magic_token:
            raise HTTPException(status_code=404, detail="Share link not found")

        audit_logger = AuditLogger(db)
        await token_repo.revoke(token_id)

        # Log revocation
        await audit_logger.log_share_link_revoked(
            organization_id=magic_token.organization_id,
            token_id=token_id,
            ip_address=request.client.host if request.client else None,
        )

        await db.commit()

        return {"status": "success", "message": "Share link revoked"}


# Audit Log Endpoints


@router.get("/audit/events", response_model=AuditEventList)
async def list_audit_events(
    org_id: UUID,
    skip: int = 0,
    limit: int = 100,
    action: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> AuditEventList:
    """Query audit events for an organization."""
    async with SessionLocal() as db:
        event_repo = AuditEventRepository(db)
        events = await event_repo.list_by_organization(
            org_id, skip, limit, action, start_date, end_date
        )

        return AuditEventList(
            items=[
                AuditEventRead(
                    id=e.id or org_id,
                    organization_id=e.organization_id,
                    actor_user_id=e.actor_user_id,
                    actor_type=e.actor_type,
                    action=e.action,
                    resource_type=e.resource_type,
                    resource_id=e.resource_id,
                    resource_name=e.resource_name,
                    changes=e.changes,
                    status=e.status,
                    reason=e.reason,
                    ip_address=e.ip_address,
                    created_at=e.created_at,
                )
                for e in events
            ],
            total=len(events),
            skip=skip,
            limit=limit,
        )


@router.get("/audit/events/{event_id}", response_model=AuditEventRead)
async def get_audit_event(event_id: UUID) -> AuditEventRead:
    """Get a specific audit event."""
    async with SessionLocal() as db:
        event_repo = AuditEventRepository(db)
        event = await event_repo.get_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Audit event not found")

        return AuditEventRead(
            id=event.id or event_id,
            organization_id=event.organization_id,
            actor_user_id=event.actor_user_id,
            actor_type=event.actor_type,
            action=event.action,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            resource_name=event.resource_name,
            changes=event.changes,
            status=event.status,
            reason=event.reason,
            ip_address=event.ip_address,
            created_at=event.created_at,
        )


@router.get("/audit/summary", response_model=AuditEventSummary)
async def get_audit_summary(org_id: UUID) -> AuditEventSummary:
    """Get audit summary for an organization."""
    async with SessionLocal() as db:
        event_repo = AuditEventRepository(db)
        summary = await event_repo.get_summary(org_id)

        from typing import cast

        return AuditEventSummary(
            events_today=cast(int, summary.get("events_today", 0)),
            total_events=cast(int, summary.get("total_events", 0)),
            action_counts=cast(dict[str, int], summary.get("action_counts", {})),
        )


@router.get("/audit/events/device/{device_id}", response_model=AuditEventList)
async def list_device_audit_events(
    device_id: UUID, skip: int = 0, limit: int = 100
) -> AuditEventList:
    """Get audit events for a specific device."""
    async with SessionLocal() as db:
        event_repo = AuditEventRepository(db)
        events = await event_repo.list_by_resource(device_id, skip, limit)

        return AuditEventList(
            items=[
                AuditEventRead(
                    id=e.id or device_id,
                    organization_id=e.organization_id,
                    actor_user_id=e.actor_user_id,
                    actor_type=e.actor_type,
                    action=e.action,
                    resource_type=e.resource_type,
                    resource_id=e.resource_id,
                    resource_name=e.resource_name,
                    changes=e.changes,
                    status=e.status,
                    reason=e.reason,
                    ip_address=e.ip_address,
                    created_at=e.created_at,
                )
                for e in events
            ],
            total=len(events),
            skip=skip,
            limit=limit,
        )


@router.get("/audit/events/user/{user_id}", response_model=AuditEventList)
async def list_user_audit_events(user_id: UUID, skip: int = 0, limit: int = 100) -> AuditEventList:
    """Get audit events for a specific user."""
    async with SessionLocal() as db:
        event_repo = AuditEventRepository(db)
        events = await event_repo.list_by_actor(user_id, skip, limit)

        return AuditEventList(
            items=[
                AuditEventRead(
                    id=e.id or user_id,
                    organization_id=e.organization_id,
                    actor_user_id=e.actor_user_id,
                    actor_type=e.actor_type,
                    action=e.action,
                    resource_type=e.resource_type,
                    resource_id=e.resource_id,
                    resource_name=e.resource_name,
                    changes=e.changes,
                    status=e.status,
                    reason=e.reason,
                    ip_address=e.ip_address,
                    created_at=e.created_at,
                )
                for e in events
            ],
            total=len(events),
            skip=skip,
            limit=limit,
        )
