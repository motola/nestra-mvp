# scripts/

Developer scripts.

## Database

The schema is managed by **Alembic** (`backend/alembic/`) — it runs automatically
on backend startup, so there is **no manual SQL step**. Supabase is just the
Postgres host: create a project, then set your connection details in
`backend/.env`:

```
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

`fresh_install.sql` and `migrate.sql` are **legacy** manual-SQL scripts from before
Alembic became the source of truth. They're kept for reference only — do not run
them against an Alembic-managed database (they'd duplicate what Alembic owns).

## Type contract

`export_openapi.py` dumps the backend's OpenAPI spec to `shared/openapi.json`, the
input for generating the cross-language TypeScript types in `shared/api.ts`.
Usually run via **`make types`** from `backend/`.
