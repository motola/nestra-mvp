# AlphaCon

A B2B platform that connects property-management organisations to their
smart-home infrastructure through a single, vendor-agnostic control layer.

Instead of juggling one app per device brand, an operator manages every
device — Govee, LIFX, Shelly, Matter — through one consistent API and UI.

---

## SPIRE — the device standard

At the core is **SPIRE** (_Smart Property Interoperability REsources_), a
FHIR-inspired, vendor-agnostic model for smart-home devices. Every device, from
any vendor, is represented as one `SpireDevice` resource: a stable identity,
business identifiers, lifecycle status, capabilities (_traits_), placement, and
live state — grouped so the structure documents who owns each field.

SPIRE lives in its own dependency-free package (`backend/src/spire/`) and is
designed to be extracted and reused:

```python
from spire import SpireDevice, Trait, VendorAdapter

# Adding a new vendor is just implementing one contract:
class MyVendorAdapter(VendorAdapter):
    async def list_devices(self) -> list[SpireDevice]: ...
    async def get_device_state(self, device_id: str) -> SpireDevice: ...
    async def send_command(self, device_id: str, command: dict) -> bool: ...
```

A device describes itself by **what it can do** (its _traits_: `on_off`,
`dimmable`, `color`, `reports_motion`, `reports_leak`, …), not by a fixed
"type" — so the platform reasons about any device uniformly, regardless of who
made it.

### What makes it interoperable, not just consistent

Every trait has a **formal spec** in `TRAIT_CATALOG`: which key it occupies in a
device's `state`, the value's unit/type, and (for actuators) the canonical
commands it accepts. So all implementations agree — brightness always lives at
`state["brightness"]` as a `percent`, set via the `set_brightness` command.

```python
from spire import SpireDevice, TRAIT_CATALOG, Command, commands_for

device.traits          # [on_off, dimmable] — what it can do
device.trait_states()  # [{trait: dimmable, value: 80, unit: "percent"}, …] — typed current state
commands_for(device.traits)             # ["turn_on", "turn_off", "set_brightness"]
Command(action="set_brightness", value=80)
```

SPIRE models the whole property, not just devices. Its resources are **`Device`**,
**`Property`**, **`Room`**, **`Occupant`**, and **`Event`** (the time-series of
what devices report — leaks, motion, low battery…).

---

## Architecture

```
backend/src/
├── spire/          The SPIRE standard — resources, traits, the adapter contract.
│                   No app or vendor dependencies; extractable as its own package.
├── integrations/   Plugins — one self-contained adapter per vendor, each
│                   implementing spire.VendorAdapter (govee · lifx · shelly · matter).
└── (app)           The product — API, persistence, auth, properties, alerts, insights.
```

The **backend is frontend-agnostic**: it is a pure JSON API (FastAPI). The
included Next.js app is one consumer — any frontend (web, mobile, third-party)
can attach. See [Attaching a frontend](#attaching-a-frontend).

---

## Quick start

### Backend (FastAPI)

```bash
cd backend
pip install -e ".[dev]"
make dev          # → http://localhost:8000  (interactive docs at /docs)
```

It runs in **demo mode** without a database or Redis — useful for a quick look.

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev       # → http://localhost:3000
```

---

## Attaching a frontend

The backend is consumed over HTTP, so any frontend can use it:

1. Point your frontend at the backend URL.
2. Set the `CORS_ORIGINS` env var on the backend to include your frontend's
   origin (comma-separated).
3. Authenticate to get a token, then call the API:

```js
const res = await fetch("https://your-api/api/v1/devices", {
  headers: { Authorization: `Bearer ${token}` },
});
const devices = await res.json(); // [{ id, vendor, name, type, online, traits, state, … }]
```

Every endpoint and the exact response shapes are documented live at **`/docs`**
(and machine-readable at `/openapi.json`) — enough to build a client without
reading the source.

For TypeScript frontends, **`shared/api.ts`** holds types generated from the
backend's OpenAPI (run `make types` from `backend/` to regenerate). Importing
those means your frontend types **cannot drift** from the backend:

```ts
import type { components } from "@/../shared/api";
type Device = components["schemas"]["DeviceResponse"];
```

---

## Tests

```bash
cd backend
make test                                          # app + integration tests
python -m unittest discover -s src -p "test_*.py"  # the spire package's own tests
```

```bash
cd frontend
npm run test
```

CI (GitHub Actions) runs lint, type-checks, and the full test suite on every push.

---

## Tech stack

- **Backend** — Python 3.12, FastAPI, SQLModel / SQLAlchemy 2.0 (async), Pydantic v2, Alembic
- **Data** — Postgres (via Supabase), Redis (via Upstash)
- **Frontend** — Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui, TanStack Query
- **Tooling** — ruff, mypy, Vitest, GitHub Actions
