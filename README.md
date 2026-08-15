# Nestra MVP — Multi-Service Smart Home Architecture

A modern microservices platform for smart home device management and intelligent automation built with a unified backend, AI intelligence service, and interactive React frontend.

## 🏗️ Architecture Overview

Nestra follows a clean three-service architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend (3000)                  │
│              (Next.js, TypeScript, UI Components)           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼──────────┐
│  Backend (8000)  │    │ Intelligence (8001)│
│   FastAPI        │◄──►│  Claude API Calls  │
│   Device APIs    │    │  Reasoning Engine  │
│   Adapters       │    │  Automation Logic  │
└─────────┬────────┘    └────────────────────┘
          │
    ┌─────▼──────────────────┐
    │  PostgreSQL Database   │
    │  (Organizations, Devices,
    │   Integrations, Users)
    └────────────────────────┘
```

**Key Design Principles:**

- **Unified device model**: All integrations normalize to a single `Device` schema
- **Vendor-agnostic**: Add new smart home vendors without modifying core architecture
- **AI-first**: Intelligence service has direct access to device state for automated actions
- **Type-safe**: Full TypeScript on frontend, mypy-checked Python backend

---

## 📁 Project Structure

### Root Directory

```
nestra-mvp/
├── backend/              # FastAPI service (devices, integrations, state)
├── intelligence/         # Claude-powered reasoning & automation
├── frontend/             # React/Next.js UI (3000)
├── shared/               # Shared utilities across services
├── docker-compose.yml    # Local dev environment
└── README.md            # This file
```

---

## 🔧 Backend Service (`backend/`)

RESTful API for device management, integrations, and state synchronization.

### Structure

```
backend/
├── src/
│   ├── main.py                      # FastAPI app entrypoint
│   ├── config.py                    # Environment & settings
│   ├── identity/                    # User & org authentication
│   │   ├── api/                     # Login, register endpoints
│   │   ├── domain/                  # Auth models & enums
│   │   └── repository/              # Database access layer
│   ├── property/                    # Properties & rooms
│   │   ├── api/routes.py            # Unified device endpoints
│   │   ├── domain/                  # Device model (unified across vendors)
│   │   └── repository/              # Device persistence
│   ├── integrations/                # Smart home vendor adapters
│   │   ├── shelly/                  # Smart plugs & switches
│   │   │   ├── adapter.py           # Shelly RPC client
│   │   │   ├── models.py            # ORM models
│   │   │   ├── schemas.py           # Pydantic schemas
│   │   │   ├── routes.py            # API endpoints
│   │   │   └── README.md
│   │   ├── govee/                   # Smart lighting
│   │   ├── lifx/                    # LIFX lights
│   │   ├── matter/                  # Matter protocol devices
│   │   ├── august/                  # Smart locks
│   │   ├── bluetooth/               # BLE scanning
│   │   └── [others]/
│   └── utility/                     # Database, logging, shared utils
├── tests/                           # Unit & integration tests
├── alembic/                         # Database migrations
├── .env                             # PostgreSQL URL, API keys
├── requirements.txt                 # Python dependencies
└── run_tests.py                     # Test runner script
```

### Running the Backend

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## 🧠 Intelligence Service (`intelligence/`)

Autonomous reasoning service that interprets device state and executes automations.

### Structure

```
intelligence/
├── src/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Settings, environment
│   ├── api/
│   │   └── routes.py            # Conversation & automation endpoints
│   ├── clients/
│   │   ├── claude_client.py      # Claude API wrapper
│   │   └── backend_client.py     # Calls backend /properties/{id}/devices
│   └── services/
│       ├── conversation.py       # Natural language understanding
│       └── automation.py         # Rule execution engine
├── .env                          # ANTHROPIC_API_KEY, DATABASE_URL, etc.
└── requirements.txt
```

### Running the Service

```bash
cd intelligence
python -m uvicorn src.main:app --reload --port 8001
# Runs on http://localhost:8001
```

---

## 🎨 Frontend (`frontend/`)

Interactive React/Next.js UI for managing properties, devices, and automations.

### Key Features

**Demo Mode Toggle**

- When **ON**: Uses fixture data from `lib/fixtures.ts` (properties, devices, integrations)
- When **OFF**: Fetches live data from backend APIs

**Device Fetching Hook**

```tsx
const { devices, loading, error } = useDevices("p_maple");
// Fetches from GET /properties/p_maple/devices
```

### Running the Frontend

```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
```

---

## 🌐 Integration Adapter Pattern

Adding a new smart home vendor (e.g., Philips Hue):

### 1. Implement adapter (`adapter.py`)

```python
class HueAdapter:
    vendor = "hue"

    async def fetch_devices(self, *, organization_id, property_id, integration_id):
        """Fetch devices from Hue Bridge API."""
        return list[Device]

    async def fetch_state(self, device: Device) -> Device:
        """Refresh device state."""
        return device

    async def execute(self, device: Device, command: str, params: dict):
        """Execute command (turn on/off, set brightness, etc)."""
        pass
```

### 2. Define schemas (`schemas.py`)

```python
class HueDeviceOut(BaseModel):
    id: UUID
    name: str
    online: bool
    raw_state: dict[str, Any]
```

### 3. Add routes (`routes.py`)

```python
router = APIRouter(prefix="/integrations/hue", tags=["hue"])

@router.get("/devices")
async def list_hue_devices(property_id: UUID):
    return devices
```

### 4. Register in `backend/src/property/api/routes.py`

```python
from integrations.hue import router as hue_router
router.include_router(hue_router)
```

**Device list endpoint auto-aggregates** via `/properties/{id}/devices`!

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional)

### Quick Start

```bash
# 1. Start all services with tmux
tmux new-session -d -s dev \
  -c backend 'python -m uvicorn src.main:app --reload --port 8000' \; \
  new-window -c intelligence 'python -m uvicorn src.main:app --reload --port 8001' \; \
  new-window -c frontend 'npm start'

# 2. Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
# Intelligence: http://localhost:8001

# 3. Attach to tmux
tmux attach -t dev
```

---

## 🔌 API Reference

### Backend

- `GET /properties/{property_id}/devices` — List all devices
- `POST /integrations/{vendor}/devices` — Add device
- `POST /integrations/{vendor}/devices/{id}/on` — Turn on
- `POST /integrations/{vendor}/devices/{id}/off` — Turn off

### Intelligence

- `POST /conversations` — Start conversation
- `POST /conversations/{id}/messages` — Send message
- `GET /automations` — List automations
- `POST /automations` — Create rule

---

## 📝 Environment Variables

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/alphacon_dev

# Intelligence
ANTHROPIC_API_KEY=sk-ant-...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📚 Technology Stack

| Layer        | Technology                                     |
| ------------ | ---------------------------------------------- |
| Frontend     | React 18, Next.js 14, TypeScript, Tailwind CSS |
| Backend      | FastAPI, SQLAlchemy, Pydantic, asyncpg         |
| Intelligence | Python 3.12, Claude API, FastAPI               |
| Database     | PostgreSQL 15                                  |
| DevOps       | Docker, Uvicorn                                |

---

## 🤝 Contributing

1. Branch: `git checkout -b feat/NEM-XX-description`
2. Commit: `NEM-XX: lowercase description`
3. Push and create PR

Pre-commit hooks enforce code quality (ruff, prettier, ESLint, commitlint).

---

**Last updated:** July 17, 2026
**Maintainer:** Akin Ola
