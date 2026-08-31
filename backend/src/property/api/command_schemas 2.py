"""API request/response schemas for command execution."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommandCreate(BaseModel):
    """Request to create and execute a command."""

    device_id: UUID = Field(..., description="Device to command")
    capability_code: str = Field(
        ..., description="Capability code (on_off, brightness, temperature, etc)"
    )
    command_type: str = Field(
        default="set_value", description="Command type (set_value, toggle, execute)"
    )
    parameters: dict[str, object] = Field(default_factory=dict, description="Command parameters")
    priority: str = Field(default="normal", description="Priority level (low, normal, high)")


class CommandRead(BaseModel):
    """Command response."""

    id: UUID
    organization_id: UUID
    device_id: UUID
    integration_id: UUID
    capability_code: str
    command_type: str
    parameters: dict[str, object]
    priority: str
    status: str = Field(..., description="Command status (pending, executing, succeeded, failed)")
    result: dict[str, object] | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    executed_at: datetime | None = None

    model_config = {"from_attributes": True}


class CommandExecute(BaseModel):
    """Response after executing a command."""

    command_id: UUID
    status: str = Field(..., description="Execution status (succeeded, failed)")
    result: dict[str, object] | None = None
    error_message: str | None = None
    executed_at: datetime


class CommandHistoryItem(BaseModel):
    """An item in command execution history."""

    id: UUID
    command_id: UUID
    status: str
    result: dict[str, object] | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommandList(BaseModel):
    """List response with commands."""

    items: list[CommandRead]
    total: int
    skip: int
    limit: int


class CommandHistoryList(BaseModel):
    """List response with command execution history."""

    items: list[CommandHistoryItem]
    total: int
