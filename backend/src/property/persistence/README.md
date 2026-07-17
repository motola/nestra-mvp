# Property Persistence

SQLAlchemy ORM models for database tables.

## Models

### DeviceModel

Maps to `devices` table in PostgreSQL.

**Columns:**

- `id` (UUID, PK) — Device ID
- `organization_id` (UUID, FK) — Owner organization (multi-tenant)
- `property_id` (UUID, FK) — Associated property
- `integration_id` (UUID, FK) — Vendor integration reference
- `device_type` (String) — DeviceType enum value
- `vendor` (String) — Vendor name ("august", "bluetooth", etc)
- `vendor_specific_id` (String) — Vendor's device ID
- `vendor_name` (String) — Friendly name from vendor
- `online` (Boolean) — Current online status
- `last_sync` (DateTime) — Last state refresh
- `created_at` (DateTime) — Created timestamp
- `updated_at` (DateTime) — Updated timestamp
- `raw_state` (JSON) — Vendor-specific metadata

**Constraints:**

- Unique constraint on `(property_id, vendor_specific_id)` — no duplicate IDs per property
- Foreign keys to `organizations`, `properties`, `integrations`

## Adding Migrations

1. Create Alembic migration:

   ```bash
   cd backend
   alembic revision --autogenerate -m "NEM-XX: add device column"
   ```

2. Review migration in `alembic/versions/`

3. Apply:
   ```bash
   alembic upgrade head
   ```

## Related

- Domain models: `backend/src/property/domain/README.md`
- Repository (uses these ORM models): `backend/src/property/repository/README.md`
- Database: `backend/src/db/README.md`
