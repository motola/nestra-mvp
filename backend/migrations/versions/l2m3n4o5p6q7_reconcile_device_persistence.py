"""Reconcile legacy device tables with the canonical ORM schema.

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-09-05

This migration is deliberately additive.  Production has tables created by the
schema-redesign migration whose shape predates the current ORM; legacy columns
are retained so old application versions can continue to run during rollout.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "l2m3n4o5p6q7"
down_revision = "k1l2m3n4o5p6"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _add(table: str, column: sa.Column[object]) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def upgrade() -> None:
    now = sa.text("CURRENT_TIMESTAMP")

    # The ORM binds DeviceType values as the native devicetype enum. Older
    # databases kept this column as VARCHAR, which makes otherwise valid ORM
    # inserts fail at runtime. Convert it in place without dropping the table.
    device_type = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT udt_name FROM information_schema.columns "
                "WHERE table_schema = current_schema() "
                "AND table_name = 'devices' AND column_name = 'device_type'"
            )
        )
        .scalar_one()
    )
    if device_type != "devicetype":
        op.execute(
            "ALTER TABLE devices ALTER COLUMN device_type TYPE devicetype "
            "USING lower(device_type::text)::devicetype"
        )

    # device_placements used placed_at in the production redesign.
    _add("device_placements", sa.Column("placement_type", sa.String(50), nullable=True))
    _add("device_placements", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE device_placements SET placement_type = 'room' WHERE placement_type IS NULL")
    source = "placed_at" if "placed_at" in _columns("device_placements") else "updated_at"
    op.execute(
        "UPDATE device_placements SET created_at = "
        f"COALESCE({source}, updated_at, CURRENT_TIMESTAMP) "
        "WHERE created_at IS NULL"
    )
    op.alter_column("device_placements", "placement_type", nullable=False, server_default="room")
    op.alter_column("device_placements", "created_at", nullable=False, server_default=now)
    if "placed_at" in _columns("device_placements"):
        op.alter_column("device_placements", "placed_at", server_default=now)

    # Some deployed databases have external_device_id/last_seen_at instead.
    _add(
        "device_integrations",
        sa.Column("connection_identifier", sa.String(500), nullable=True),
    )
    _add("device_integrations", sa.Column("discovered_at", sa.DateTime(timezone=True)))
    _add("device_integrations", sa.Column("last_synced_at", sa.DateTime(timezone=True)))
    di_cols = _columns("device_integrations")
    identifier = "external_device_id" if "external_device_id" in di_cols else "device_id::text"
    discovered = "created_at" if "created_at" in di_cols else "CURRENT_TIMESTAMP"
    synced = "last_seen_at" if "last_seen_at" in di_cols else "updated_at"
    op.execute(
        "UPDATE device_integrations SET connection_identifier = "
        f"COALESCE(connection_identifier, {identifier}), "
        f"discovered_at = COALESCE(discovered_at, {discovered}, CURRENT_TIMESTAMP), "
        f"last_synced_at = COALESCE(last_synced_at, {synced})"
    )
    op.alter_column("device_integrations", "connection_identifier", nullable=False)
    op.alter_column("device_integrations", "discovered_at", nullable=False, server_default=now)

    # Canonical capability fields are additive to the richer legacy catalog.
    _add("capabilities", sa.Column("name", sa.String(255), nullable=True))
    _add("capabilities", sa.Column("description", sa.String(500), nullable=True))
    _add("capabilities", sa.Column("category", sa.String(100), nullable=True))
    op.execute("UPDATE capabilities SET name = code WHERE name IS NULL")
    op.execute("UPDATE capabilities SET category = 'general' WHERE category IS NULL")
    op.alter_column("capabilities", "name", nullable=False)
    op.alter_column("capabilities", "category", nullable=False)
    if "updated_at" in _columns("capabilities"):
        op.alter_column("capabilities", "updated_at", server_default=now)

    # Legacy device capability fields are intentionally retained. Defaults
    # let the canonical ORM write rows without knowing those compatibility
    # columns exist.
    device_capability_columns = _columns("device_capabilities")
    if "source" in device_capability_columns:
        op.alter_column("device_capabilities", "source", server_default="discovery")
    if "config" in device_capability_columns:
        op.alter_column(
            "device_capabilities",
            "config",
            server_default=sa.text("'{}'::jsonb"),
        )
    if "updated_at" in device_capability_columns:
        op.alter_column("device_capabilities", "updated_at", server_default=now)

    # Preserve device_current_state while materialising the ORM's plural table.
    inspector = sa.inspect(op.get_bind())
    if "device_current_states" not in inspector.get_table_names():
        op.create_table(
            "device_current_states",
            sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
            sa.Column(
                "device_id",
                PGUUID(as_uuid=True),
                sa.ForeignKey("devices.id", ondelete="CASCADE"),
                nullable=False,
                unique=True,
            ),
            sa.Column("state", sa.JSON(), nullable=False),
            sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        if "device_current_state" in inspector.get_table_names():
            op.execute(
                "INSERT INTO device_current_states "
                "(id, device_id, state, last_updated_at, created_at, updated_at) "
                "SELECT device_id, device_id, state, observed_at, updated_at, updated_at "
                "FROM device_current_state "
                "ON CONFLICT (device_id) DO NOTHING"
            )

    # Retain event history and expose it through canonical columns.
    _add("device_state_events", sa.Column("state_change", sa.JSON(), nullable=True))
    _add("device_state_events", sa.Column("event_type", sa.String(50), nullable=True))
    _add("device_state_events", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    event_cols = _columns("device_state_events")
    value = "value::json" if "value" in event_cols else "'{}'::json"
    event_type = "source" if "source" in event_cols else "'state_change'"
    observed = "observed_at" if "observed_at" in event_cols else "CURRENT_TIMESTAMP"
    op.execute(
        f"UPDATE device_state_events SET state_change = COALESCE(state_change, {value}), "
        f"event_type = COALESCE(event_type, {event_type}), "
        f"created_at = COALESCE(created_at, {observed})"
    )
    op.alter_column("device_state_events", "state_change", nullable=False)
    op.alter_column("device_state_events", "event_type", nullable=False)
    op.alter_column("device_state_events", "created_at", nullable=False, server_default=now)
    if "capability_code" in event_cols:
        op.alter_column("device_state_events", "capability_code", server_default="state")
    if "value" in event_cols:
        op.alter_column(
            "device_state_events",
            "value",
            server_default=sa.text("'{}'::jsonb"),
        )
    if "source" in event_cols:
        op.alter_column("device_state_events", "source", server_default="api")
    if "observed_at" in event_cols:
        op.alter_column("device_state_events", "observed_at", server_default=now)

    op.execute("UPDATE devices SET raw_state = '{}'::json WHERE raw_state IS NULL")
    op.alter_column("devices", "raw_state", nullable=False, server_default=sa.text("'{}'::json"))
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_devices_org_integration_vendor_key "
        "ON devices (organization_id, integration_id, vendor, vendor_specific_id)"
    )


def downgrade() -> None:
    # Forward-only reconciliation: legacy and canonical data must not be dropped.
    op.execute("DROP INDEX IF EXISTS uq_devices_org_integration_vendor_key")
