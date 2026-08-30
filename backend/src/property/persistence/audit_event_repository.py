"""Audit event repository for compliance logging."""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.audit import AuditEvent
from property.repository.models import AuditEventModel

logger = logging.getLogger(__name__)


class AuditEventRepository:
    """Persist and query audit events (append-only)."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: AuditEvent) -> AuditEvent:
        """Create a new audit event."""
        event.id = uuid4()

        model = AuditEventModel(
            id=event.id,
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
            user_agent=event.user_agent,
            created_at=event.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return event

    async def get_by_id(self, event_id: UUID) -> AuditEvent | None:
        """Get an audit event by ID."""
        result = await self._session.execute(
            select(AuditEventModel).where(AuditEventModel.id == event_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def list_by_organization(
        self,
        org_id: UUID,
        skip: int = 0,
        limit: int = 100,
        action: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AuditEvent]:
        """Query audit events for an organization."""
        query = select(AuditEventModel).where(AuditEventModel.organization_id == org_id)

        if action:
            query = query.where(AuditEventModel.action == action)

        if start_date:
            query = query.where(AuditEventModel.created_at >= start_date)

        if end_date:
            query = query.where(AuditEventModel.created_at <= end_date)

        query = query.order_by(AuditEventModel.created_at.desc()).offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_resource(
        self, resource_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditEvent]:
        """List all events for a specific resource."""
        result = await self._session.execute(
            select(AuditEventModel)
            .where(AuditEventModel.resource_id == resource_id)
            .order_by(AuditEventModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_actor(
        self, actor_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditEvent]:
        """List all events performed by a user."""
        result = await self._session.execute(
            select(AuditEventModel)
            .where(AuditEventModel.actor_user_id == actor_id)
            .order_by(AuditEventModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def get_summary(self, org_id: UUID) -> dict[str, object]:
        """Get audit summary for an organization."""
        from datetime import UTC

        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Count events today
        result = await self._session.execute(
            select(AuditEventModel).where(
                and_(
                    AuditEventModel.organization_id == org_id,
                    AuditEventModel.created_at >= today_start,
                )
            )
        )
        today_events = len(result.scalars().all())

        # Count by action (all time)
        result = await self._session.execute(
            select(AuditEventModel).where(AuditEventModel.organization_id == org_id)
        )
        all_events = result.scalars().all()

        action_counts: dict[str, int] = {}
        for event in all_events:
            action = str(event.action)
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "events_today": today_events,
            "total_events": len(all_events),
            "action_counts": action_counts,
        }

    @staticmethod
    def _model_to_domain(model: AuditEventModel) -> AuditEvent:
        """Convert ORM model to domain model."""
        return AuditEvent(
            id=model.id,
            organization_id=model.organization_id,
            actor_user_id=model.actor_user_id,
            actor_type=model.actor_type,
            action=model.action,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            resource_name=model.resource_name,
            changes=model.changes,
            status=model.status,
            reason=model.reason,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            created_at=model.created_at,
        )
