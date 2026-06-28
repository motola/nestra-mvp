"""Typed request/response contracts for the devices API.

These are the shapes the frontend depends on. Keeping them as explicit models
(rather than ``dict[str, Any]``) means FastAPI validates and documents every
response, and a change to the contract is a visible change here.
"""

from __future__ import annotations

from datetime import datetime
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


class DeviceResponse(BaseModel):
    """The flat device shape the list/get endpoints return (``SpireDevice.to_api()``).

    This is the typed contract the frontend consumes — and what the generated
    cross-language types in ``shared/`` are produced from.
    """

    id: str
    vendor_id: str
    vendor: str
    name: str
    type: str
    online: bool
    controllable: bool
    state: dict[str, Any]
    power_draw: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    leak_detected: bool | None = None
    property_id: str | None = None
    room_id: str | None = None
    last_seen: datetime
    supported_commands: list[str]
    traits: list[str]
