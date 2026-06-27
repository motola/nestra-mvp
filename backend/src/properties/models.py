"""Property model — a managed unit (flat, HMO room, short-let property)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PropertyStatus = Literal["all_clear", "needs_attention", "critical"]


class Property(BaseModel):
    """A property managed by an organisation on the Alphacon platform."""

    id: str
    name: str
    address: str
    organisation_id: str | None = None
    device_count: int = 0
    alert_count: int = 0
    status: PropertyStatus = "all_clear"
    is_demo: bool = False


class PropertyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)
    organisation_id: str | None = None
