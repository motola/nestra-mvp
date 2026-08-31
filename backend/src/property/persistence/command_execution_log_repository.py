"""Command execution log repository — append-only logging of command executions."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.command import CommandExecutionLogEntry, CommandStatus
from property.repository.models import CommandExecutionLogModel

logger = logging.getLogger(__name__)


class CommandExecutionLogRepository:
    """Persist and retrieve command execution logs (append-only)."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        command_id: UUID,
        status: CommandStatus,
        result: dict[str, object] | None = None,
        error_message: str | None = None,
    ) -> CommandExecutionLogEntry:
        """Log a command execution (append-only)."""
        now = datetime.now(UTC)
        log_id = uuid4()

        model = CommandExecutionLogModel(
            id=log_id,
            command_id=command_id,
            status=status,
            result=result,
            error_message=error_message,
            created_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_command(self, command_id: UUID) -> list[CommandExecutionLogEntry]:
        """Get all execution log entries for a command, in chronological order."""
        result = await self._session.execute(
            select(CommandExecutionLogModel)
            .where(CommandExecutionLogModel.command_id == command_id)
            .order_by(CommandExecutionLogModel.created_at)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    @staticmethod
    def _model_to_domain(model: CommandExecutionLogModel) -> CommandExecutionLogEntry:
        """Convert ORM model to domain model."""
        return CommandExecutionLogEntry(
            id=model.id,
            command_id=model.command_id,
            status=model.status,
            result=model.result,
            error_message=model.error_message,
            created_at=model.created_at,
        )
