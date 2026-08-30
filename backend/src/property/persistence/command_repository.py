"""Command repository — persistence and retrieval of device commands."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.command import Command, CommandStatus
from property.repository.models import CommandModel

logger = logging.getLogger(__name__)


class CommandRepository:
    """Persist and retrieve device commands."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, command_id: UUID) -> Command | None:
        """Get a command by ID."""
        result = await self._session.execute(
            select(CommandModel).where(CommandModel.id == command_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, command: Command) -> Command:
        """Create a new command."""
        now = datetime.now(UTC)
        command.id = uuid4()
        command.created_at = now
        command.updated_at = now

        model = CommandModel(
            id=command.id,
            organization_id=command.organization_id,
            device_id=command.device_id,
            integration_id=command.integration_id,
            capability_code=command.capability_code,
            command_type=command.command_type,
            parameters=command.parameters,
            priority=command.priority,
            status=command.status,
            result=command.result,
            error_message=command.error_message,
            created_at=now,
            updated_at=now,
            executed_at=command.executed_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def update_status(
        self,
        command_id: UUID,
        status: CommandStatus,
        result: dict[str, object] | None = None,
        error_message: str | None = None,
    ) -> Command | None:
        """Update command status and result."""
        model = await self._session.get(CommandModel, command_id)
        if not model:
            return None

        now = datetime.now(UTC)
        model.status = status
        model.result = result
        model.error_message = error_message
        model.updated_at = now

        if status == CommandStatus.SUCCEEDED or status == CommandStatus.FAILED:
            model.executed_at = now

        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_device(
        self, device_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Command], int]:
        """Get paginated command history for a device."""
        # Get total count
        count_result = await self._session.execute(
            select(CommandModel).where(CommandModel.device_id == device_id)
        )
        total = len(count_result.scalars().all())

        # Get paginated results
        result = await self._session.execute(
            select(CommandModel)
            .where(CommandModel.device_id == device_id)
            .order_by(desc(CommandModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models], total

    async def list_pending(self, skip: int = 0, limit: int = 100) -> tuple[list[Command], int]:
        """Get paginated list of pending commands."""
        # Get total count
        count_result = await self._session.execute(
            select(CommandModel).where(CommandModel.status == CommandStatus.PENDING)
        )
        total = len(count_result.scalars().all())

        # Get paginated results
        result = await self._session.execute(
            select(CommandModel)
            .where(CommandModel.status == CommandStatus.PENDING)
            .order_by(
                desc(CommandModel.priority),
                CommandModel.created_at,
            )
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models], total

    async def list_by_status(
        self,
        status: CommandStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Command], int]:
        """Get paginated list of commands by status."""
        # Get total count
        count_result = await self._session.execute(
            select(CommandModel).where(CommandModel.status == status)
        )
        total = len(count_result.scalars().all())

        # Get paginated results
        result = await self._session.execute(
            select(CommandModel)
            .where(CommandModel.status == status)
            .order_by(desc(CommandModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models], total

    async def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Command], int]:
        """Get paginated list of commands for an organization."""
        # Get total count
        count_result = await self._session.execute(
            select(CommandModel).where(CommandModel.organization_id == organization_id)
        )
        total = len(count_result.scalars().all())

        # Get paginated results
        result = await self._session.execute(
            select(CommandModel)
            .where(CommandModel.organization_id == organization_id)
            .order_by(desc(CommandModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models], total

    async def cancel(self, command_id: UUID) -> Command | None:
        """Cancel a pending command."""
        model = await self._session.get(CommandModel, command_id)
        if not model or model.status != CommandStatus.PENDING:
            return None

        model.status = CommandStatus.CANCELLED
        model.updated_at = datetime.now(UTC)
        await self._session.flush()
        return self._model_to_domain(model)

    @staticmethod
    def _model_to_domain(model: CommandModel) -> Command:
        """Convert ORM model to domain model."""
        return Command(
            id=model.id,
            organization_id=model.organization_id,
            device_id=model.device_id,
            integration_id=model.integration_id,
            capability_code=model.capability_code,
            command_type=model.command_type,
            parameters=model.parameters,
            priority=model.priority,
            status=model.status,
            result=model.result,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
            executed_at=model.executed_at,
        )
