"""Automation triggers — event-based triggers for automation rules."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class TriggerType(StrEnum):
    """Type of trigger for automation."""

    TIME_BASED = "time_based"  # Runs at specific times
    OCCUPANCY_BASED = "occupancy_based"  # Triggers on occupancy changes
    STATE_BASED = "state_based"  # Triggers on device state changes
    MANUAL = "manual"  # Manual trigger (user-initiated)


class Trigger(BaseModel):
    """A trigger condition for automation."""

    id: UUID | None = None
    organization_id: UUID
    automation_id: UUID
    trigger_type: TriggerType
    condition: dict[str, object] = Field(default_factory=dict)
    # Examples:
    # time_based: {"hour": 9, "minute": 0, "days": ["monday", "tuesday"]}
    # occupancy_based: {"event": "arrival", "property_id": "..."}
    # state_based: {"device_id": "...", "capability": "on_off", "state": "on"}
    enabled: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"frozen": False}


class AutomationAction(BaseModel):
    """An action to execute when a trigger fires."""

    id: UUID | None = None
    automation_id: UUID
    device_id: UUID
    capability_code: str  # "on_off", "brightness", "temperature", etc.
    command_type: str  # "set_value", "toggle", "execute"
    parameters: dict[str, object] = Field(default_factory=dict)
    delay_seconds: int = 0  # Delay before execution
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"frozen": False}


class AutomationRule(BaseModel):
    """An automation rule linking triggers to actions."""

    id: UUID | None = None
    organization_id: UUID
    property_id: UUID
    name: str
    description: str | None = None
    triggers: list[Trigger] = Field(default_factory=list)
    actions: list[AutomationAction] = Field(default_factory=list)
    enabled: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"frozen": False}
