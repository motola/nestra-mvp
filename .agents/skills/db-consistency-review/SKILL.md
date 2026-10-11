---
name: db-consistency-review
description: Review database-backed changes across domain models, SQLAlchemy ORM, Alembic migrations, repositories, API schemas/routes, and frontend contracts. Use for every PR that changes persistence models, migrations, database writes, tenant-scoped endpoints, or frontend payloads backed by persisted data.
---

# Database Consistency Review

Treat this as an end-to-end runtime review, not a file-by-file style review.

## Required review path

1. Identify every changed persisted entity and trace it through:
   `frontend request -> API schema -> route -> domain -> repository -> ORM -> migration -> PostgreSQL`.
2. Trace the read path back to every frontend consumer. Verify response fields, enum values,
   optionality, array/object shape, endpoint method, and URL are identical at both ends.
3. For each write, verify all required database columns are supplied by the ORM or have a safe
   server default. Include legacy columns retained during forward-only migrations.
4. Compare each domain model field with its canonical ORM column. Compare ORM names, types,
   nullability, enums, foreign keys, uniqueness, and defaults with the migrated schema.
5. Verify tenant identity comes from the authenticated JWT and every tenant-scoped query executes
   inside `org_scope`. Do not trust a frontend-supplied organization ID.

## Migration gates

Run these from `backend` against a disposable PostgreSQL 16 database:

```bash
alembic heads
alembic history
alembic upgrade head
python scripts/check_db_consistency.py
python scripts/check_bluetooth_contract.py
```

Require exactly one root and one head. Reject duplicate revision IDs, missing parents, cycles,
or edits that delete already-published migration history. Prefer forward-only, in-place `ALTER`
operations. Never drop and recreate a populated table unless data preservation is explicitly
designed and tested.

Test both:

- an empty database upgraded from the first revision;
- a production-shaped database at the previous head upgraded to the new head.

## Runtime gates

- Exercise the actual authenticated endpoint, not only repository unit tests.
- Verify the write can be read through the exact endpoint used by the UI.
- Verify retries are idempotent or return an intentional conflict, never an unexplained 500.
- Verify expected relationship and audit rows are persisted in the same transaction.
- Run Ruff, mypy, frontend type-check, and relevant backend/frontend tests.

## Review output

Report blocking findings first with exact file and line references. For each finding, state the
request that triggers it, the failing layer, and the expected runtime error. Do not approve while
any missing table/column/type, broken migration chain, endpoint mismatch, tenant leak, or untested
write/read path remains.
