"""SPIRE property resources — the places devices live and who is present.

The device resource describes *what* is installed; these resources describe
*where* it is installed and *who* is there. A ``SpireProperty`` is a managed
building or unit, a ``SpireRoom`` is a subdivision of one, and a
``SpireOccupant`` is a person present at the property (tenant, guest, or staff).
Together with ``SpireDevice`` they let SPIRE model a property as a whole, not
just its hardware.

Like the device resource, each carries an ``AuditMeta`` for system-managed
provenance, and logical ids are stable business keys assigned by the caller.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from spire.device import AuditMeta


class SpireProperty(BaseModel):
    """A managed building or unit — the top-level place devices and people belong to."""

    resource_type: Literal["Property"] = "Property"
    id: str
    organization_id: str | None = None
    name: str
    address: str | None = None
    timezone: str | None = None
    meta: AuditMeta = Field(default_factory=AuditMeta)


class SpireRoom(BaseModel):
    """A subdivision of a property — a room or zone a device can be placed in."""

    resource_type: Literal["Room"] = "Room"
    id: str
    property_id: str
    name: str
    floor: int | None = None
    meta: AuditMeta = Field(default_factory=AuditMeta)


class SpireOccupant(BaseModel):
    """A person present at a property — a tenant, guest, or staff member."""

    resource_type: Literal["Occupant"] = "Occupant"
    id: str
    property_id: str
    room_id: str | None = None
    name: str
    email: str | None = None
    phone: str | None = None
    meta: AuditMeta = Field(default_factory=AuditMeta)
