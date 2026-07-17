# Database Configuration

PostgreSQL database setup, connection pooling, and Alembic migrations.

## Connection

PostgreSQL connection string from environment:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/nestra
```

## SQLAlchemy Setup

Configured in `shared/db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

## Alembic Migrations

Track schema changes with Alembic (already configured).

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "NEM-XX: add column"
```

### Review Migration

Alembic generates migration files in `alembic/versions/`. Review the generated SQL before applying.

### Apply Migrations

```bash
alembic upgrade head
```

### Downgrade

```bash
alembic downgrade -1
```

## Tables

### organizations

- `id` (UUID, PK)
- `name` (String)
- `created_at`, `updated_at` (DateTime)

### users

- `id` (UUID, PK)
- `email` (String, unique)
- `password_hash` (String)
- `display_name` (String)
- `organization_id` (UUID, FK)
- `role` (String enum: admin, editor, viewer)
- `created_at`, `updated_at` (DateTime)

### integrations

- `id` (UUID, PK)
- `organization_id` (UUID, FK)
- `vendor` (String: "august", "bluetooth", etc)
- `account_identifier` (String)
- `enabled` (Boolean)
- `created_at`, `updated_at` (DateTime)

### devices

- `id` (UUID, PK)
- `organization_id` (UUID, FK)
- `property_id` (UUID, FK)
- `integration_id` (UUID, FK)
- `device_type` (String enum)
- `vendor` (String)
- `vendor_specific_id` (String)
- `vendor_name` (String)
- `online` (Boolean)
- `last_sync` (DateTime)
- `raw_state` (JSON)
- `created_at`, `updated_at` (DateTime)

## Row-Level Security (RLS)

PostgreSQL RLS policies ensure:

- Users only see resources in their organization
- Policies are set on all tables with `organization_id`

Example RLS policy (future):

```sql
CREATE POLICY org_isolation ON devices
FOR SELECT USING (organization_id = current_user_org_id());
```

## Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost/nestra
DB_ECHO=false  # Set to 'true' for SQL logging in debug mode
```

## Related

- Shared utilities: `backend/src/shared/README.md`
- Backend overview: `backend/src/README.md`
