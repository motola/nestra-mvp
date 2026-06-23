# Claude Code — Backend Prompt

*The system prompt for Claude Code when working on the AlphaCon backend. Use this when starting a Claude Code session by passing it as the first message or including it via `claude.md` at the repo root.*

*Companion file: `backend/SKILL.md` — Claude Code reads it automatically via skill discovery when touching backend files. Both reinforce the same rules: this prompt is the deep brief, `SKILL.md` is the always-on reminder.*

---

You are working on **AlphaCon AI**, a B2B SaaS platform connecting property management organisations to their smart-home infrastructure through an AI control layer. Backend is **Python 3.12 + FastAPI + Postgres + Redis + ARQ**.

## Your operating principles

1. **Read the architecture first, then write.** Before producing any code, read `docs/glossary.md`, `docs/class_diagrams.md`, and the relevant bounded-context's `__init__.py`. Don't reinvent.
2. **Never write spaghetti.** Module boundaries are sacred. Bounded contexts cannot import each other's internals. Cross-context calls go through public types only (re-exported from each context's `__init__.py`).
3. **Tests are not optional.** Every module you touch must have at least one test before you finish. Use Python's standard-library `unittest` (not pytest).
4. **Five files maximum per turn.** If a task needs more, propose splitting it into batches and stop. Don't power through.
5. **Show your reasoning before code.** Briefly say what you're going to do, why, what you're not going to do, and which files you'll touch. Then produce the files.
6. **Preserve invariants.** Every aggregate root carries `organization_id`. Every tenant-scoped table has RLS. Every endpoint goes through the tenant scope middleware. Never bypass these.

## Code conventions

- **Python**: 3.12, type hints on every public signature, `from __future__ import annotations` at top of every file
- **Linting**: `ruff check` and `ruff format` must pass; the pre-commit hook will block commits otherwise
- **Imports**: absolute, sorted by ruff's default isort profile. No `from x import *`.
- **No comments that restate the code.** Comments explain *why*, not *what*. Prefer good names and short functions.
- **Functions ≤ 30 lines** as a strong default. Refactor before exceeding.
- **No magic strings or numbers.** Constants in module-level `Final[str]` or in enums.
- **Async by default** for any I/O (DB, HTTP, Redis). Sync only for pure CPU.
- **Return Pydantic models** from API endpoints. Never raw dicts.
- **Pydantic v2 syntax** only (`BaseModel`, `Field`, `field_validator`, etc.). No v1 leftovers.

## File structure (do not deviate)

```
backend/
  src/
    identity/                    # Bounded context: Identity & Access
      __init__.py                # Public exports only (Organization, User, etc.)
      domain/                    # Aggregate roots, value objects, domain logic
        organization.py
        user.py
        portfolio.py
        ...
      repository/                # Persistence (SQLAlchemy + RLS)
        organization_repo.py
        ...
      services/                  # Use cases (signup, login)
        signup.py
        ...
      api/                       # FastAPI routes
        routes.py
        schemas.py
      tests/                     # unittest TestCases
        test_organization.py
        ...

    properties_devices_occupancy/  # Bounded context: Property/Device/Stay/Tenant
      ...same shape...

    integrations/                # Bounded context: Integration
      ...

    agent/                       # Bounded context: Agent / AI
      ...

    automations/                 # Bounded context: Automation
      ...

    audit/                       # Bounded context: Audit & Events
      ...

    shared/                      # Cross-cutting
      types.py                   # ActorRef, ResourceOwnerRef
      polymorphic.py             # Owner type resolution
      db.py                      # org_scope context manager
      errors.py                  # Common exception base classes
      events.py                  # EventBus

    main.py                      # FastAPI app entry, mounts routes from each context
    config.py                    # Settings via pydantic-settings
    dependencies.py              # FastAPI dependencies (auth, tenant scope)

  alembic/                       # Migrations
    versions/

  tests/                         # Cross-cutting / integration tests
    test_rls_isolation.py        # MUST exist and pass

  pyproject.toml
  SKILL.md                       # Always-on convention reminder for Claude Code
```

## Forbidden patterns

- ❌ Cross-context imports of internals (e.g., `from alphacon.identity.domain.organization import Organization` from inside `alphacon.agent`). If you need it, re-export from `alphacon.identity.__init__` and import from there.
- ❌ Direct ORM queries that bypass the tenant scope middleware. Always use `async with org_scope(session, organization_id):` or rely on the FastAPI dependency.
- ❌ Hardcoded role strings. Use the `OrgRole`, `PortfolioRole`, `PropertyRole` enums.
- ❌ Inline SQL strings except in migrations. Use SQLAlchemy expressions.
- ❌ `print()` statements. Use the structured logger from `shared/logging.py`.
- ❌ Catching `Exception` broadly. Catch specific exceptions or let them propagate.
- ❌ `# type: ignore` without a comment explaining why. If you need it, justify it.
- ❌ Assertions in production code paths. Assertions are for tests only.

## When you're stuck or unsure

If the architecture doesn't tell you what to do, **stop and ask**. Don't invent. Examples of times to stop:

- A new bounded context dependency would be needed
- A cross-context join in a query
- A change to the polymorphic owner pattern
- A new role or permission level
- A schema change that touches multiple aggregates
- Anything involving the agent's tool catalog filtering

For these, propose the change and wait for approval before implementing.

## Output format for every task

```
## Plan
- What I'll do, in 3–6 bullets
- What I'm explicitly not doing
- Files I'll touch (≤ 5)

## Files

### path/to/first/file.py
[full file contents]

### path/to/second/file.py
[full file contents]

...

## Tests

[unittest TestCase covering the change]

## Verification
- How to run the tests
- Any manual verification steps
- Any follow-ups for next batch
```
