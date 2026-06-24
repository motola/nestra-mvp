# backend/SKILL.md

*Always-on conventions for the AlphaCon backend. Claude Code re-reads this when touching `backend/` files. The deep brief is `prompts/claude_code_backend.md`; this is the condensed reminder. Both are subordinate to the root `CLAUDE.md` and the architecture docs — those are the source of truth.*

**Stack:** Python 3.12 · FastAPI · Postgres (Supabase) · SQLAlchemy 2.0 async + asyncpg · Pydantic v2 · Redis (Upstash) · ARQ · Anthropic Claude.

---

## Operating rules (non-negotiable)

1. **Read the architecture before writing.** `docs/glossary.md`, `docs/class_diagrams.md`, and the relevant context's `__init__.py`. Don't reinvent or guess vocabulary.
2. **Five files maximum per turn.** More than that → propose splitting into batches and stop.
3. **Show your plan before code** (`## Plan` → files → `## Tests` → `## Verification`).
4. **Tests are not optional.** Every module you touch gets at least one `unittest` TestCase before you finish. Not pytest.
5. **Preserve the invariants:** every tenant-scoped aggregate carries `organization_id`; every tenant table has RLS; every endpoint passes through the tenant-scope middleware. Never bypass these.
6. **Stop and ask** for: new cross-context dependency, cross-context join, change to the polymorphic owner pattern, new role/permission, multi-aggregate schema change, new third-party dependency, anything touching the agent's tool catalog or the audit log structure.

## Target structure — six bounded contexts

`identity/` · `properties_devices_occupancy/` · `integrations/` · `agent/` · `automations/` · `audit/`, plus `shared/`. Each context: `domain/ repository/ services/ api/ tests/`. Public types are re-exported from each context's `__init__.py`; cross-context code imports only from there.

## Code conventions

- `from __future__ import annotations` at the top of every file.
- Type hints on every public signature.
- `ruff check` and `ruff format` must pass (pre-commit blocks otherwise).
- Absolute, sorted imports. No `from x import *`.
- Comments explain **why**, never restate **what**. Prefer good names + short functions.
- Functions ≤ 30 lines (strong default).
- No magic strings/numbers — module-level `Final` constants or enums.
- Async by default for all I/O (DB, HTTP, Redis). Sync only for pure CPU.
- Endpoints return Pydantic models, never raw dicts. Pydantic v2 only.

## Forbidden

- ❌ Cross-context imports of internals — re-export from the context `__init__.py` instead.
- ❌ ORM queries that bypass tenant scope — use `async with org_scope(session, organization_id):` or the FastAPI dependency.
- ❌ Hardcoded role strings — use `OrgRole` / `PortfolioRole` / `PropertyRole` enums.
- ❌ Inline SQL except in Alembic migrations — use SQLAlchemy expressions.
- ❌ `print()` — use the structured logger.
- ❌ Broad `except Exception` — catch specific exceptions or let them propagate.
- ❌ `# type: ignore` without a justifying comment.
- ❌ Assertions in production code paths (tests only).

## Hard rules (must never break)

1. All vendor adapters extend `BaseVendorAdapter` in `src/integrations/__init__.py`.
2. All vendor normalisers output `AlphaconDevice` only.
3. Nothing outside `integrations/` references vendor field names.
4. Demo data lives only in `src/demo/`; `DEMO_MODE` (env) controls all demo
   behaviour, and demo is additionally gated per-request by `X-Show-Demo` so
   customers never see it (see `api/dependencies.get_effective_settings`).
5. Never store or log WiFi passwords.
6. Never expose `SUPABASE_SERVICE_ROLE_KEY` to the frontend.
7. Never display IP addresses in API responses that reach the frontend.
8. All database tables are created automatically on startup.
9. If the database is unavailable at startup, log and continue.

## Current state (mid-migration — do not assume the target structure exists yet)

The build predates this structure and is being brought into line with the docs. As of this writing: code is laid out flat (`src/api/v1/`, `src/models/`, `src/services/`, `src/integrations/`, `src/demo/`), **not** in bounded-context folders. Auth (User/Session/JWT), RLS, the `org_scope` manager, ARQ workers, and Alembic migrations (the `versions/` folder is empty) **do not exist yet**. The agent (`api/v1/chat.py`) is a single Claude call, not a tool-use loop. When you add new work, build it in the documented structure; when you touch old code, migrate it toward the docs rather than extending the flat layout. See `docs/progress.md` for what's done vs. outstanding.
