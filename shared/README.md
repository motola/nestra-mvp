# shared/

Cross-language contract shared between the backend and the frontend.

This is the single source of truth for API types: TypeScript types are generated
from the backend's Pydantic models so the two sides never drift. The frontend
imports from here instead of hand-writing request/response shapes.

- **Generated, not hand-edited** — types here are produced from `backend/` Pydantic
  models (generation pipeline lands in a later batch). Do not edit generated files
  by hand.
- **No runtime code** — types and contracts only. No business logic, no secrets.

See `docs/mvp_scope.md` (Shared) and `prompts/claude_code_frontend.md` for how the
frontend consumes these types.
