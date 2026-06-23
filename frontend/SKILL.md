# frontend/SKILL.md

*Always-on conventions for the AlphaCon frontend. Claude Code re-reads this when touching `frontend/` files. The deep brief is `prompts/claude_code_frontend.md`; this is the condensed reminder. Both are subordinate to the root `CLAUDE.md`, `prompts/claude_design.md`, and `frontend/DESIGN_SYSTEM.md` — those are the source of truth.*

**Stack:** Next.js 15 (App Router) · TypeScript 5 strict · Tailwind CSS 4 · shadcn/ui · TanStack Query · react-hook-form + zod.

---

## Operating rules (non-negotiable)

1. **Read the design system before writing.** `prompts/claude_design.md` and `frontend/DESIGN_SYSTEM.md` (tokens, component conventions). Don't invent design.
2. **Five files maximum per turn.** More → propose splitting and stop.
3. **Show your plan before code** (`## Plan` → files → `## Tests` → `## Verification`).
4. **Tests are not optional.** Vitest for unit/component, Playwright for end-to-end. Every component ships with at least basic coverage.
5. **Stop and ask** for: a new shadcn component, a new colour/spacing/font-weight token, a page layout outside the marketing/auth/app/tenant patterns, or anything touching the AI agent UI (special rules apply).

## Code & component conventions

- **Server Components by default.** `"use client"` only when interactivity is needed, with a one-line comment justifying it.
- **No data fetching in components.** All API calls go through TanStack Query hooks in `lib/api/`. No `useEffect`/`useState` for server state. No hand-rolled `fetch`.
- **Generated types only** — from `shared/`. Never hand-write request/response types.
- TypeScript strict; no `any` without an eslint-disable + justification (prefer `unknown` + narrow).
- `@/` path alias; `eslint` + `prettier` must pass.
- Comments explain **why**. Functions ≤ 30 lines. One component per file (filename matches default export).
- Forms use `react-hook-form` + `zod`. Loading, empty, and error states are first-class on every screen.

## Design & copy rules

- Restraint over decoration — we sell to property managers, not consumers.
- Sentence case everywhere. No emojis, no exclamation marks, no "Welcome aboard!" energy.
- Buttons name the action: "Add property", not "Submit". Errors are calm and specific.
- The AI agent speaks in lower case: "i can help with that. which property?"

## Forbidden

- ❌ Inline styles / `style={{ }}` — Tailwind classes only.
- ❌ Tailwind values outside the design tokens — propose adding a token instead of inventing.
- ❌ `useEffect`/`useState` for server state; hand-rolled fetch; hand-written API types.
- ❌ Components handling auth state directly — use the auth provider.
- ❌ A new shadcn component without proposing it first.
- ❌ Glassmorphism, neumorphism, gradients (except AI agent avatars), Lottie/particle effects, emojis in production UI.

## Current state (mid-migration — do not assume the target structure exists yet)

The build predates parts of this spec. As of this writing: it uses **Radix UI primitives directly, not shadcn/ui**; the API client is a single flat `lib/api.ts` (not `lib/api/` with per-hook files); types are hand-mirrored in `lib/types.ts` (no `shared/` generation pipeline); routes are flat under `app/` (no `(marketing)`/`(auth)`/`(app)`/`(tenant)` route groups); there is **no auth UI** (no login/signup/dashboard-gated shell). When you add new work, build it in the documented structure; when you touch old code, migrate it toward the docs. See `docs/progress.md` for status.
