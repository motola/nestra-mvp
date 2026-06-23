# AlphaCon AI — Foundational MVP Scope

*The walking skeleton. What we build first, what we defer, what "done" looks like.*

---

## What this document is

The foundational MVP is the smallest end-to-end working version of AlphaCon AI that proves the architecture, validates the developer workflow, and gives us something we can iterate on. **It is not the Phase 1 product.** It is the spine. Phase 1 features layer on top of it.

If you're reading this and tempted to add a feature to the MVP scope: don't. The whole point is that we ship the spine first, then bolt features on as separate, reviewable batches.

---

## What "foundational MVP" means in concrete terms

A user can:

1. Sign up for an account (creates an Organization + a default Portfolio)
2. Log in
3. Add a single Property to their default Portfolio
4. See a dashboard listing their Property
5. Log out

That's it. **Five user stories. No devices yet. No integrations yet. No agent yet. No tenants yet. No automations yet.**

What this proves:
- The full request flow works end-to-end (frontend → API → database → response)
- Authentication and session management work
- The bounded-context module structure is correct
- Multi-tenancy isolation (Row-Level Security) actually works
- The CI pipeline catches issues
- Pre-commit hooks block secrets and lint failures
- Frontend and backend type-share through the `shared/` folder works
- Deployment to Fly.io works
- The codebase is approachable for the next contributor

Once the spine is alive, every Phase 1 feature (devices, integrations, agent, automations) is a vertical slice we add without restructuring the foundation.

---

## In scope (build it)

### Backend
- FastAPI app with health check endpoint
- Identity & Access bounded context (just enough for MVP):
  - `User` aggregate
  - `Organization` aggregate
  - `Portfolio` aggregate
  - `OrgMembership` linking User to Organization
  - `Session` (JWT-based)
  - `User.can()` permission resolver (signature only — full implementation comes later)
- Property bounded context (just enough for MVP):
  - `Property` aggregate (with `address` value object)
- Auth middleware (JWT validation, sets the active organization on the request)
- Tenant scope middleware (sets Postgres `app.current_organization_id` for RLS)
- Endpoints:
  - `POST /auth/signup` — creates User + Organization + default Portfolio + OrgMembership atomically
  - `POST /auth/login` — issues JWT
  - `POST /auth/logout` — revokes session
  - `GET /me` — returns current user + organization
  - `POST /properties` — creates a property in the user's default portfolio
  - `GET /properties` — lists user's accessible properties
- Postgres schema (Alembic migrations) with RLS policies on all tenant-scoped tables
- One end-to-end smoke test that signs up, logs in, creates a property, lists it, logs out

### Frontend
- Next.js 15 app with TypeScript and Tailwind
- shadcn/ui set up with the design tokens from `prompts/claude_design.md`
- Pages:
  - `/` — landing page (very minimal)
  - `/signup` — signup form
  - `/login` — login form
  - `/dashboard` — authenticated home, shows organization + property list
  - `/dashboard/properties/new` — add a property form
- Auth state managed via cookies + a small auth provider
- Type-safe API client that consumes types from `shared/`
- One Playwright end-to-end test covering the signup → property → logout flow

### Shared
- TypeScript types generated from backend Pydantic models (one source of truth)
- Generated client SDK so the frontend never hand-writes API call signatures

### Tooling & infrastructure
- Monorepo with `frontend/`, `backend/`, `shared/`, `infra/`, `prompts/`, `docs/`
- GitHub Actions CI: lint + unittest + frontend tests + type-check on every push
- Pre-commit hooks: ruff (Python lint+format), eslint (TS lint), gitleaks (secrets scan), commitlint
- Local dev: `make dev` brings up backend + frontend + Postgres + Redis via Docker Compose
- Deploy targets defined but not deployed yet (Fly.io for backend, Vercel for frontend)

---

## Explicitly out of scope (do NOT build)

These all belong to AlphaCon's eventual Phase 1 product, but **not the foundational MVP**:

- ❌ Devices, Integrations, vendor adapters (Nest, Hue, etc.)
- ❌ The AI agent / Claude integration / tool-use loop
- ❌ Stays, Tenants, magic-link auth
- ❌ Automations (triggers, conditions, actions)
- ❌ Audit log queries / UI (the writing happens in MVP, viewing comes later)
- ❌ Billing / subscriptions / Stripe
- ❌ Email beyond a transactional confirmation on signup
- ❌ Portfolios with multiple Properties (default-portfolio-only for MVP UI)
- ❌ Inviting other users / Memberships UI
- ❌ Property Assignments / Contractor flows
- ❌ Multi-room support inside a Property
- ❌ Mobile app (Phase 1 deliverable, not foundational MVP)
- ❌ Magic link / SSO (password-based auth for MVP, magic link comes when Tenants land)
- ❌ Production deployment (we'll deploy after the foundation is approved end-to-end)

If a feature isn't on the "in scope" list above, it's deferred. Period.

---

## Success criteria — how we know the MVP is done

All of the following must be true before we move to feature work:

- [ ] A new contributor can clone the repo, run one command, and have everything running locally inside 10 minutes
- [ ] CI pipeline runs green on `main` (lint, type-check, unittest, frontend tests)
- [ ] Pre-commit hooks block secrets being committed (verified with a deliberate test commit)
- [ ] Pre-commit hooks block lint failures (verified)
- [ ] A test user can sign up, log in, create a property, list it, and log out — through the actual UI in a browser
- [ ] An RLS test proves that User A cannot see User B's properties even with manually crafted SQL
- [ ] Backend Pydantic types are auto-exported to TypeScript and consumed by the frontend (verified by deleting and regenerating)
- [ ] Module boundaries enforced: backend bounded contexts cannot import each other's internals (verified by a ruff/import-linter rule)
- [ ] No secrets in any committed file
- [ ] README explains what the project is and how to run it
- [ ] All four `prompts/` files are present and the SKILL.md files explain conventions for both frontend and backend

When all of these are checked, the foundational MVP is done. We then start **vertical slice 1: Devices** as a separate batch sequence.

---

## Why we built it this way

A few decisions worth flagging that someone might second-guess later:

**Why not just start with devices and the agent right away?**
Because they're the most complex parts. Building them on top of broken foundations means we'd refactor twice — once when the foundations break, once when we add real complexity. Building them on top of a proven foundation means we add them as a single clean vertical slice.

**Why a default Portfolio in the MVP UI instead of just Property?**
Because the data model already has Portfolio. Hiding it from the UI is fine; pretending it doesn't exist in the schema would create exactly the kind of refactor we're avoiding. Auto-create on signup, hide in UI, surface later when needed.

**Why password auth instead of magic-link from day one?**
Operators and admins (the MVP user) want password auth. Magic link is for tenants, who aren't part of the MVP scope. Adding magic link later is a one-day job because Supabase Auth supports both natively.

**Why Playwright + Vitest on frontend but unittest on backend?**
Per project decision. The TypeScript ecosystem doesn't have a `unittest` equivalent, and Vitest + Playwright is the modern standard. Backend uses Python's standard-library `unittest` for portability and zero new dependencies.

---

## Batch sequencing

The foundational MVP ships across these batches (max 5 files per batch):

1. **Batch 1 (this one)** — Strategy: scope, accounts, prompts. No code.
2. **Batch 2** — Monorepo skeleton, pre-commit, CI config.
3. **Batch 3** — Backend skeleton: pyproject, FastAPI app entry, module folders, smoke test.
4. **Batch 4** — Frontend skeleton: Next.js app, design tokens, base shadcn setup.
5. **Batch 5** — Backend Identity context: User + Organization + Portfolio aggregates + signup endpoint.
6. **Batch 6** — Backend Property context: Property aggregate + endpoints + RLS policies.
7. **Batch 7** — Frontend signup + login flows (the auth UI).
8. **Batch 8** — Frontend dashboard + property list + create-property form.
9. **Batch 9** — End-to-end smoke test (Playwright) + final RLS isolation test.
10. **Batch 10** — README, contributor docs, dev environment polish.

Each batch is reviewable and approvable on its own. Each unblocks the next.

After Batch 10, foundational MVP is done. We then start vertical slices for actual product features.
