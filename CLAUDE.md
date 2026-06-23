# CLAUDE.md
 
*Repo root entry point. Claude Code reads this automatically at the start of every session. Read it carefully — it tells you what this project is, where everything lives, and how to work here.*
 
---
 
## What you are working on
 
**AlphaCon AI** is a B2B SaaS platform that connects property management organisations to their smart-home infrastructure through an AI-driven control layer. It is currently in early development. We are building a foundational MVP — the walking skeleton — before any feature work.
 
Read `docs/mvp_scope.md` for the precise definition of what's in scope right now. **Do not add features that are not in that scope, even if they would be useful.** Scope discipline is the single most important rule on this project.
 
## Repository layout
 
This is a monorepo:
 
```
nestra-mvp/
├── CLAUDE.md                    ← you are here
├── README.md                    ← human-facing project intro
├── docs/                        ← project documentation (read these first)
├── prompts/                     ← deep-brief prompts to read at session start
├── backend/                     ← Python / FastAPI service
│   └── SKILL.md                 ← always-on backend conventions
├── frontend/                    ← Next.js / TypeScript app
│   └── SKILL.md                 ← always-on frontend conventions
├── shared/                      ← cross-language types (TS generated from Pydantic)
└── infra/                       ← deployment & CI config
```
 
## Before you start any task
 
Read these in order:
 
1. **`docs/mvp_scope.md`** — what we're building, what we're not. If a task contradicts this, stop and flag it.
2. **`docs/glossary.md`** — domain vocabulary. `Organization`, `Portfolio`, `Property`, `Stay`, `Tenant`, etc. Use these terms consistently.
3. **`docs/class_diagrams.md`** — entity relationships and bounded contexts.
4. **The deep-brief prompt for the side you're working on:**
   - For backend tasks: `prompts/claude_code_backend.md`
   - For frontend tasks: `prompts/claude_code_frontend.md`
5. **The relevant `SKILL.md`** for the folder you're touching (`backend/SKILL.md` or `frontend/SKILL.md`) — these are also re-read automatically when you edit files in those folders.
If a task spans both backend and frontend, read both deep-brief prompts.
 
If a document is referenced but doesn't exist yet, say so before you proceed. Don't fabricate content.
 
## How we work in this repo
 
### Five files maximum per turn
 
Every batch of work touches at most five files. If a task needs more, **stop and propose splitting it** into multiple batches. Do not power through. The point of small batches is human review and approval — bypassing that is the fastest way to introduce bugs that are expensive to remove later.
 
### Show your plan before code
 
Every response that produces code starts with a `## Plan` section. Format:
 
```
## Plan
- What I'll do, in 3–6 bullets
- What I'm explicitly not doing
- Files I'll touch (≤ 5)
```
 
Then the actual files, then the tests, then a `## Verification` section explaining how to confirm it works.
 
### Tests are not optional
 
Every module you touch must have at least one test before you finish.
 
- Backend: Python's standard-library `unittest` module (not pytest). Test files at `backend/<context>/tests/test_<thing>.py`.
- Frontend: Vitest for unit/component tests, Playwright for end-to-end. Test files at `frontend/tests/`.
If you can't test something easily, that's a signal the design is wrong. Refactor; don't skip the test.
 
### Pre-commit hooks will block bad commits
 
The repo has pre-commit hooks that run on every commit. If they fail, your commit is blocked. They check:
 
- Secrets (gitleaks) — no API keys or passwords in any committed file
- Lint and format (ruff for Python, eslint + prettier for TypeScript)
- Commit message format (Conventional Commits)
Don't bypass them with `--no-verify`. If a hook is failing legitimately, fix the issue. If it's a false positive, raise it before bypassing.
 
### CI must stay green
 
GitHub Actions runs on every push:
- Lint and format checks
- Type checks (mypy for Python, tsc for TypeScript)
- Backend `unittest` suite
- Frontend Vitest + Playwright suites
If you make a change that breaks CI, fix it in the same PR. Don't merge red.
 
## Stop and ask
 
These situations are not for you to invent. Stop and ask before producing code:
 
- A new bounded context dependency
- A cross-context join in a query
- A change to the polymorphic owner pattern (Device, Integration, Automation)
- A new role or permission level (`OrgRole`, `PortfolioRole`, `PropertyRole`, `TenantRole`)
- A schema change that touches multiple aggregates
- A new third-party service or dependency
- A new design token (colour, spacing, typography) on the frontend
- A new shadcn/ui component on the frontend
- Anything involving the AI agent's tool catalog or visibility scope
- Anything involving the audit log's structure
- Any deviation from the file structure documented in the deep-brief prompts
Saying "I'm not sure, can we pause?" is always the right call. Inventing architecture is always the wrong one.
 
## Things you can safely assume
 
- Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Alembic
- Postgres via Supabase (with pgvector and Row-Level Security)
- Redis via Upstash
- ARQ for background jobs
- Next.js 15 App Router, TypeScript 5 strict, Tailwind CSS 4, shadcn/ui
- TanStack Query for data fetching
- react-hook-form + zod for forms
- AWS KMS for credential envelope encryption
- AWS SES + Resend for email
- Cloudflare for DNS, CDN, WAF, R2, Workers, Turnstile
- Anthropic Claude API for the AI agent
- Voyage AI for embeddings
- Fly.io for backend hosting (when we deploy — not yet)
- Vercel for frontend hosting (when we deploy — not yet)
- GitHub Actions for CI
## Code style summary
 
This is the lightweight version. Full rules in the `SKILL.md` files.
 
- **Type hints on every public signature**, both Python and TypeScript
- **Functions ≤ 30 lines** as a strong default
- **No comments that restate the code** — explain *why*, not *what*
- **No magic strings or numbers** — use enums or `Final` constants
- **Async by default** for I/O on the backend
- **Server Components by default** on the frontend
- **No emojis in production UI**
- **Sentence case** for all UI copy
- **Tailwind classes only** — no inline styles, no invented colours
## What "done" looks like for any task
 
A task is done when all of the following are true:
 
- [ ] All new and changed code has tests
- [ ] All tests pass locally (`make test` or equivalent)
- [ ] Pre-commit hooks pass without `--no-verify`
- [ ] Lint and format pass
- [ ] Type checks pass
- [ ] Documentation updated if behaviour or interface changed
- [ ] No secrets in any committed file
- [ ] No `print()` or `console.log()` left behind
- [ ] No `# type: ignore` or `// @ts-ignore` without a comment justifying it
- [ ] No `TODO` comments without a linked issue or follow-up batch noted
If any of those aren't true, the task isn't done — even if the code "works."
 
## A final note
 
The architecture has been carefully designed before any code was written. Read the docs. Trust the structure. The five-files-per-turn rule and the stop-and-ask rule exist to protect that investment. They are not bureaucracy; they are how this project ships without becoming spaghetti.
 
Welcome to AlphaCon. Let's build something that lasts.
 