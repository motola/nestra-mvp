"""Typed request/response contracts for the devices API.

These are the shapes the frontend depends on. Keeping them as explicit models
(rather than ``dict[str, Any]``) means FastAPI validates and documents every
response, and a change to the contract is a visible change here.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

# ── Requests ──────────────────────────────────────────────────────────────────


class MatterCommandPayload(BaseModel):
    command: str  # "on_off" | "brightness" | "color_temperature"
    value: Any = None


class ControlPayload(BaseModel):
    command: str  # "turn_on" | "turn_off"
    value: Any = None


class AssignRoomPayload(BaseModel):
    room_id: str | None


# ── Responses ─────────────────────────────────────────────────────────────────


class DeviceCommandResult(BaseModel):
    """Outcome of a turn_on / turn_off command."""

    success: bool
    state: bool


class MatterDeviceState(BaseModel):
    """Live attribute snapshot for a Matter device."""

    device_id: str
    node_id: str
    online: bool
    on_off: bool | None = None
    brightness: int | None = None


class DeleteResult(BaseModel):
    """Confirmation that a device was removed from the registry."""

    deleted: str
