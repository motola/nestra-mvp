"""Device factory — applies sync context and invariants in one place.

An adapter interprets vendor data into a SpireDevice that knows only what the
vendor told it. The factory then stamps the operator's context onto that device
— which organisation and property it belongs to, and which integration produced
it — plus the sync timestamp. Keeping this in one function means no adapter has
to know anything about persistence or tenancy.
"""

from __future__ import annotations

from datetime import UTC, datetime

from spire.device import SpireDevice


def create_device_data(
    device: SpireDevice,
    *,
    organization_id: str | None = None,
    property_id: str | None = None,
    integration_id: str | None = None,
) -> SpireDevice:
    """Return the interpreted device with sync context and provenance applied.

    Builds in memory only — identity and the user's name are left untouched, so
    a re-sync never overwrites a rename. The repository decides insert vs update.
    """
    placement = device.placement.model_copy(
        update={
            "organization_id": organization_id or device.placement.organization_id,
            "property_id": property_id or device.placement.property_id,
        }
    )
    meta = device.meta.model_copy(
        update={
            "source": integration_id or device.meta.source,
            "last_synced_at": datetime.now(UTC),
        }
    )
    return device.model_copy(update={"placement": placement, "meta": meta})
