# shared/

Cross-language contract shared between the backend and the frontend.

This is the single source of truth for API types: `api.ts` is **generated** from
the backend's OpenAPI spec (which comes from its Pydantic models), so the two
sides never drift. The frontend imports from here instead of hand-writing
request/response shapes.

- **`api.ts`** — generated TypeScript types for every endpoint and schema. The
  device shape, for example, is `components["schemas"]["DeviceResponse"]`.
- **Generated, not hand-edited.** Regenerate with **`make types`** from `backend/`
  (it dumps the OpenAPI to `openapi.json`, then runs `openapi-typescript`). Do not
  edit `api.ts` by hand — your changes will be overwritten.
- **No runtime code** — types and contracts only. No business logic, no secrets.

`openapi.json` is an intermediate artifact and is gitignored.

The frontend can migrate off its hand-written `lib/types.ts` to these generated
types incrementally — each type replaced is one fewer place that can drift.
