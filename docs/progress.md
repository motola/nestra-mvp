# Build Progress

Tracks the foundational MVP and the work to bring the existing build into line with the architecture docs. Each batch is reviewed and approved before the next starts.

**Status legend:** ✅ Done · ⚠️ Partial / built but not to the documented structure · ⏳ Not started.

> **Reconciliation note (2026-06-21):** The build ran ahead of the documented batch sequence — devices, vendor integrations, the agent, and most app pages already exist, but in a flat layout without auth, RLS, or the six bounded contexts. The docs (`architecture.md`, `class_diagrams.md`, `glossary.md`, `CLAUDE.md`, `prompts/`) are the source of truth; the table below reflects reality, and the alignment batches that follow describe the work to close the gap. Nothing working will be deleted — existing features are treated as vertical slices to be refactored into the documented structure.

---

## Foundational sequence

| Batch | What | Status |
|---|---|---|
| 1 | Strategy — scope docs, architecture, prompts, glossary | ✅ Done (now in repo `docs/` + `prompts/` + `CLAUDE.md`) |
| 2 | Monorepo skeleton — folder structure, CI/CD, pre-commit hooks, Makefile | ✅ Done |
| 3 | Backend skeleton — pyproject, FastAPI entry, health check | ⚠️ Done but flat (`src/api`, `src/models`, `src/services`), not six bounded contexts |
| 4 | Frontend skeleton — Next.js app, design tokens, base UI | ⚠️ Done with Radix primitives, not shadcn/ui |
| 5 | Backend Identity — User, Organization, Portfolio + signup/login/JWT/sessions | ⏳ Not started (`Organisation` table exists; no User/auth/session) |
| 6 | Backend Property — Property aggregate + endpoints + RLS policies | ⚠️ Partial — Property/Room/Device CRUD exists; **RLS absent** |
| 7 | Frontend auth — signup and login flows | ⏳ Not started |
| 8 | Frontend dashboard — property list + create-property form | ⚠️ Built ahead — dashboard/properties/devices pages exist (unauthenticated) |
| 9 | End-to-end — Playwright smoke test + RLS isolation test | ⏳ Not started (one backend health smoke test only) |
| 10 | Polish — README, contributor docs, dev environment | ⚠️ Partial — Makefile/compose done; `README.md` empty |

---

## Built ahead of sequence (existing vertical slices to refactor into the documented structure)

- **Devices & control** — `Device` model, registry, state history, control/command endpoints.
- **Vendor integrations** — Govee, LIFX, Matter, Shelly adapters, all normalising to `AlphaconDevice` behind `BaseVendorAdapter`; provisioning + scanning + Matter commissioning (SSE).
- **Agent chat** — `POST /chat/` SSE streaming with portfolio context (single Haiku call; **no tool-use loop / routing / memory / prompt caching yet**).
- **Insights & intelligence** — Claude insights with Haiku/Sonnet routing + Upstash Redis caching; intelligence items list.
- **Alerts** — alert model, listing, dismiss.
- **App pages** — energy, maintenance, reports, tenants, settings (UI shells).
- **Demo mode** — `DEMO_MODE` seeds 6 properties / rooms / devices.

---

## Alignment batches (to bring the build to the docs)

| # | Work | Status |
|---|---|---|
| A0 | `backend/SKILL.md` + `frontend/SKILL.md` + reconcile this file | ✅ Done |
| A1 | Alembic baseline migration from current schema | ✅ Done — `0001_baseline_schema` (6 tables), live DB stamped to `0001`, startup clean |
| A2 | Identity context — User/Org/Portfolio/Membership/Session + signup/login/JWT | ✅ Done — `0002` applied to live DB; `/auth/signup`, `/auth/login`, `/auth/logout`, `/me` working end-to-end (bcrypt + JWT) |
| A3 | Tenant-scope middleware + RLS policies + RLS isolation test | ⚠️ Mostly done — `org_scope`/`OrgScopedSessionDep` + `0003` RLS policies applied to live DB (active, demo-safe). Isolation test written; final run pending a local Postgres (won't run against shared DB). |
| A4 | Restructure flat `src/` into six bounded contexts | ⏳ Not started |
| A5 | Agent upgrade — tool-use loop, model router, prompt caching, conversation memory | ⏳ Not started |
| A6 | `shared/` Pydantic→TS type generation + frontend auth UI | ⚠️ In progress — Auth UI done (F1+F2): `/login`, `/signup`, app gated behind auth (redirect to `/login`), Header shows real user + working sign-out. `shared/` Pydantic→TS type-gen still pending |
