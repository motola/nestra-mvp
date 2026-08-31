"""AlphaCon schema redesign - production-ready multi-tenant architecture.

Revision ID: d6e7f8g9h0i1
Revises: c520e2a2989a
Create Date: 2026-08-29

Comprehensive redesign implementing:
- Identity & Access (Users, OrgMembership, Portfolio/Property assignments)
- Property Hierarchy (Rooms as first-class entities)
- Tenant & Stay Model (StayRoom for flexible room allocation)
- Providers & Integrations (M:N device-to-integration relationships)
- Device Capabilities (normalized feature system)
- State Tracking (current + historical telemetry)
- Device Access (role-based authorization)
- Commands (unified action path for all actors)
- Audit Events (append-only audit trail)
- Extension hooks (Automation, AI)

Soft delete policy:
- Business entities: use deleted_at
- Event/append-only: no soft delete

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from alembic import op

revision: str = "d6e7f8g9h0i1"
down_revision: str | None = "c520e2a2989a"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create production schema."""

    # ========================================================================
    # Phase 1: Identity & Access
    # ========================================================================

    # Rename/extend users table (currently exists as part of identity)
    # Assuming users table exists, just ensure fields are present
    op.add_column(
        "users",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add portfolio_memberships
    op.create_table(
        "portfolio_memberships",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "portfolio_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("portfolios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_portfolio_memberships_portfolio_id",
        "portfolio_memberships",
        ["portfolio_id"],
    )
    op.create_index(
        "ix_portfolio_memberships_user_id",
        "portfolio_memberships",
        ["user_id"],
    )
    # Partial unique index for active memberships (soft delete support)
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_portfolio_memberships ON portfolio_memberships "
            "(portfolio_id, user_id) WHERE deleted_at IS NULL"
        )
    )

    # Add property_assignments
    op.create_table(
        "property_assignments",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "property_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_property_assignments_property_id",
        "property_assignments",
        ["property_id"],
    )
    op.create_index(
        "ix_property_assignments_user_id",
        "property_assignments",
        ["user_id"],
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_property_assignments ON property_assignments "
            "(property_id, user_id) WHERE deleted_at IS NULL"
        )
    )

    # ========================================================================
    # Phase 2: Property Hierarchy - Rooms
    # ========================================================================

    op.create_table(
        "rooms",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "property_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("room_type", sa.String(100), nullable=False),
        sa.Column("floor_label", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_rooms_property_id", "rooms", ["property_id"])
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_rooms_property_name ON rooms "
            "(property_id, name) WHERE deleted_at IS NULL"
        )
    )

    # ========================================================================
    # Phase 3: Tenant & Stay Model
    # ========================================================================

    op.create_table(
        "tenants",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tenants_organization_id", "tenants", ["organization_id"])
    op.create_index("ix_tenants_user_id", "tenants", ["user_id"])
    op.create_index("ix_tenants_email", "tenants", ["email"])
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_tenants_org_user ON tenants "
            "(organization_id, user_id) WHERE user_id IS NOT NULL AND deleted_at IS NULL"
        )
    )

    op.create_table(
        "stays",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "property_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("booking_source", sa.String(100), nullable=True),
        sa.Column("external_booking_id", sa.String(255), nullable=True),
        sa.Column("check_in_at", sa.Date(), nullable=False),
        sa.Column("check_out_at", sa.Date(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stays_property_id", "stays", ["property_id"])
    op.create_index("ix_stays_check_in_at", "stays", ["check_in_at"])
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_stays_booking ON stays "
            "(booking_source, external_booking_id) WHERE external_booking_id IS NOT NULL"
        )
    )

    op.create_table(
        "stay_rooms",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stay_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stays.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "room_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("rooms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_stay_rooms_stay_id", "stay_rooms", ["stay_id"])
    op.create_index("ix_stay_rooms_room_id", "stay_rooms", ["room_id"])
    op.create_unique_constraint(
        "uq_stay_rooms",
        "stay_rooms",
        ["stay_id", "room_id"],
    )

    op.create_table(
        "stay_tenants",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stay_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stays.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("access_status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stay_tenants_stay_id", "stay_tenants", ["stay_id"])
    op.create_index("ix_stay_tenants_tenant_id", "stay_tenants", ["tenant_id"])
    op.create_unique_constraint(
        "uq_stay_tenants",
        "stay_tenants",
        ["stay_id", "tenant_id"],
    )

    op.create_table(
        "stay_preferences",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stay_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stays.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("preference_key", sa.String(100), nullable=False),
        sa.Column("value", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stay_preferences_stay_id", "stay_preferences", ["stay_id"])
    op.create_unique_constraint(
        "uq_stay_preferences",
        "stay_preferences",
        ["stay_id", "preference_key"],
    )

    # ========================================================================
    # Phase 4: Providers & Integrations
    # ========================================================================

    op.create_table(
        "providers",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("provider_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_providers_slug", "providers", ["slug"])

    # Update integrations table with new fields
    op.add_column(
        "integrations",
        sa.Column(
            "provider_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("providers.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.add_column(
        "integrations",
        sa.Column("connection_identifier", sa.String(255), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("display_name", sa.String(255), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("credential_provider", sa.String(100), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("credential_ref", sa.String(500), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("oauth_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("config", JSONB(), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_integrations_provider_id", "integrations", ["provider_id"])
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_integrations_connection ON integrations "
            "(organization_id, provider_id, connection_identifier) "
            "WHERE provider_id IS NOT NULL AND deleted_at IS NULL"
        )
    )

    # ========================================================================
    # Phase 5: Device Model
    # ========================================================================

    # Update devices table
    op.add_column(
        "devices",
        sa.Column("category", sa.String(100), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("manufacturer", sa.String(255), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("model", sa.String(255), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("serial_number", sa.String(255), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("ownership_type", sa.String(50), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("owner_property_id", PGUUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("owner_tenant_id", PGUUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("status", sa.String(50), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_devices_owner_property",
        "devices",
        "properties",
        ["owner_property_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_devices_owner_tenant",
        "devices",
        "tenants",
        ["owner_tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_devices_serial ON devices "
            "(manufacturer, serial_number) WHERE serial_number IS NOT NULL AND deleted_at IS NULL"
        )
    )

    op.create_table(
        "device_placements",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "property_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "room_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("rooms.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("display_name_override", sa.String(255), nullable=True),
        sa.Column("position_metadata", JSONB(), nullable=True),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_device_placements_device_id", "device_placements", ["device_id"])
    op.create_index("ix_device_placements_property_id", "device_placements", ["property_id"])
    op.create_index("ix_device_placements_room_id", "device_placements", ["room_id"])

    op.create_table(
        "device_integrations",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "integration_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("integrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("connection_identifier", sa.String(500), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_device_integrations_device_id", "device_integrations", ["device_id"])
    op.create_index(
        "ix_device_integrations_integration_id", "device_integrations", ["integration_id"]
    )
    op.create_unique_constraint(
        "uq_device_integrations",
        "device_integrations",
        ["device_id", "integration_id"],
    )

    # ========================================================================
    # Phase 6: Capabilities
    # ========================================================================

    op.create_table(
        "capabilities",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("value_schema", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_capabilities_code", "capabilities", ["code"])

    op.create_table(
        "device_capabilities",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "capability_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_device_capabilities_device_id", "device_capabilities", ["device_id"])
    op.create_index(
        "ix_device_capabilities_capability_id", "device_capabilities", ["capability_id"]
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_device_capabilities ON device_capabilities "
            "(device_id, capability_id) WHERE deleted_at IS NULL"
        )
    )

    # ========================================================================
    # Phase 7: Device State
    # ========================================================================

    op.create_table(
        "device_current_state",
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("state", JSONB(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fresh_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_device_current_state_updated", "device_current_state", ["updated_at"])

    op.create_table(
        "device_state_events",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("capability_code", sa.String(100), nullable=False),
        sa.Column("value", JSONB(), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_device_state_events_device_id", "device_state_events", ["device_id"])
    op.create_index("ix_device_state_events_observed", "device_state_events", ["observed_at"])

    # ========================================================================
    # Phase 8: Commands
    # ========================================================================

    op.create_table(
        "commands",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "integration_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("integrations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "issued_by_user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "issued_by_stay_tenant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stay_tenants.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_type", sa.String(50), nullable=False),
        sa.Column("capability_code", sa.String(100), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("provider_command_id", sa.String(255), nullable=True),
        sa.Column("result", JSONB(), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_commands_device_id", "commands", ["device_id"])
    op.create_index("ix_commands_integration_id", "commands", ["integration_id"])
    op.create_index("ix_commands_status", "commands", ["status"])
    op.create_index("ix_commands_created", "commands", ["created_at"])

    # ========================================================================
    # Phase 9: Device Access & Magic Links
    # ========================================================================

    op.create_table(
        "device_access_grants",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stay_tenant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stay_tenants.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "device_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "room_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("rooms.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("capability_code", sa.String(100), nullable=True),
        sa.Column("permission", sa.String(50), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "granted_by_user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_device_access_grants_stay_tenant", "device_access_grants", ["stay_tenant_id"]
    )
    op.create_index("ix_device_access_grants_user", "device_access_grants", ["user_id"])
    op.create_index("ix_device_access_grants_device", "device_access_grants", ["device_id"])
    op.create_index("ix_device_access_grants_room", "device_access_grants", ["room_id"])

    op.create_table(
        "magic_link_tokens",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stay_tenant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stay_tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_magic_link_tokens_token_hash", "magic_link_tokens", ["token_hash"])
    op.create_index("ix_magic_link_tokens_stay_tenant", "magic_link_tokens", ["stay_tenant_id"])

    # ========================================================================
    # Phase 10: Audit Events (append-only)
    # ========================================================================

    op.create_table(
        "audit_events",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "actor_stay_tenant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("stay_tenants.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_type", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", PGUUID(as_uuid=True), nullable=False),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_organization", "audit_events", ["organization_id"])
    op.create_index("ix_audit_events_occurred", "audit_events", ["occurred_at"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])


def downgrade() -> None:
    """Revert all schema changes."""
    op.drop_table("audit_events")
    op.drop_table("magic_link_tokens")
    op.drop_table("device_access_grants")
    op.drop_table("commands")
    op.drop_table("device_state_events")
    op.drop_table("device_current_state")
    op.drop_table("device_capabilities")
    op.drop_table("capabilities")
    op.drop_table("device_placements")
    op.drop_table("device_integrations")

    op.drop_constraint("fk_devices_owner_tenant", "devices")
    op.drop_constraint("fk_devices_owner_property", "devices")
    op.drop_column("devices", "deleted_at")
    op.drop_column("devices", "status")
    op.drop_column("devices", "owner_tenant_id")
    op.drop_column("devices", "owner_property_id")
    op.drop_column("devices", "ownership_type")
    op.drop_column("devices", "serial_number")
    op.drop_column("devices", "model")
    op.drop_column("devices", "manufacturer")
    op.drop_column("devices", "category")

    op.drop_constraint("uq_integrations_connection", "integrations")
    op.drop_column("integrations", "deleted_at")
    op.drop_column("integrations", "config")
    op.drop_column("integrations", "oauth_expires_at")
    op.drop_column("integrations", "credential_ref")
    op.drop_column("integrations", "credential_provider")
    op.drop_column("integrations", "display_name")
    op.drop_column("integrations", "connection_identifier")
    op.drop_column("integrations", "provider_id")

    op.drop_table("providers")

    op.drop_table("stay_preferences")
    op.drop_table("stay_tenants")
    op.drop_table("stay_rooms")
    op.drop_table("stays")
    op.drop_table("tenants")

    op.drop_table("rooms")

    op.drop_table("property_assignments")
    op.drop_table("portfolio_memberships")

    op.drop_column("users", "deleted_at")
