"""Command domain models for device control execution."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class CommandStatus(StrEnum):
    """Status of a command execution."""

    PENDING = "pending"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(StrEnum):
    """Type of command to execute."""

    SET_VALUE = "set_value"
    TOGGLE = "toggle"
    EXECUTE = "execute"


class CommandPriority(StrEnum):
    """Priority level for command execution."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Command(BaseModel):
    """A device command to be executed."""

    id: UUID | None = None
    organization_id: UUID
    device_id: UUID
    integration_id: UUID
    capability_code: str  # "on_off", "brightness", "temperature", etc.
    command_type: CommandType = CommandType.SET_VALUE
    parameters: dict[str, object] = Field(default_factory=dict)  # {"brightness": 75}
    priority: CommandPriority = CommandPriority.NORMAL
    status: CommandStatus = CommandStatus.PENDING
    result: dict[str, object] | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    executed_at: datetime | None = None

    model_config = {"frozen": False}


class CommandResult(BaseModel):
    """Result of executing a command."""

    command_id: UUID
    status: CommandStatus
    result: dict[str, object] | None = None
    error_message: str | None = None
    executed_at: datetime


class CommandExecutionLogEntry(BaseModel):
    """An entry in the command execution log."""

    id: UUID | None = None
    command_id: UUID
    status: CommandStatus
    result: dict[str, object] | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"frozen": False}
