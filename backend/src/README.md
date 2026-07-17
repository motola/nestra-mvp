# Backend Architecture

FastAPI-based backend for AlphaCon smart home platform. Manages properties, devices, integrations, authentication, and AI-driven device control.

## Module Overview

```
backend/src/
├── main.py              # FastAPI app entry point
├── config.py            # Settings & environment config
├── api/                 # API layer (routers, schemas)
├── property/            # Property & device domain
├── identity/            # Authentication & users
├── intelligence/        # AI-driven device control
├── integrations/        # Third-party vendor adapters (August, Bluetooth, etc)
├── demo/                # Demo & test data endpoints
├── shared/              # Shared utilities (DB, common models)
└── db/                  # Database configuration
```

## Module Descriptions

### **property/** — Device & Property Domain

Core domain logic for managing properties and devices. Normalizes all vendor-specific device APIs into a unified `Device` schema.

- `domain/` — Domain models (Device, DeviceType)
- `api/` — HTTP endpoints for properties & devices
- `repository/` — Data access patterns
- `persistence/` — Database models
- `services/` — Business logic

**Related:** `backend/src/property/README.md`

### **integrations/** — Vendor-Specific Adapters

Factory and adapter pattern for third-party integrations (August Smart Locks, Bluetooth devices, Govee lights, etc).

Each vendor implements `IntegrationAdapter` protocol:

- `fetch_devices()` — Fetch devices from vendor API
- `fetch_state()` — Refresh device state
- `execute()` — Send control commands

Adapters normalize vendor payloads → unified Device schema.

**Related:** `backend/src/integrations/README.md`

### **intelligence/** — MOVED

AI-driven device control service has been moved to a separate microservice.

**Related:** `intelligence/README.md` (separate from backend)

### **identity/** — Authentication & Users

User and organization management, authentication, and authorization.

- `domain/` — User, Organization models
- `api/` — Auth endpoints
- `repository/` — Data access
- `services/` — Auth logic

**Related:** `backend/src/identity/README.md`

### **api/** — API Layer

HTTP router aggregation and versioning. Currently v1 is integrated directly into main.py.

**Related:** `backend/src/api/README.md`

### **shared/** — Shared Utilities

Cross-cutting concerns: database connections, base models, common utilities.

- `db.py` — SQLAlchemy Base & session config

**Related:** `backend/src/shared/README.md`

### **demo/** — Demo & Test Endpoints

Development endpoints for demoing device interactions. Not for production.

**Related:** `backend/src/demo/README.md`

## Architecture Patterns

### Adapter Pattern (Integrations)

Each third-party vendor implements `IntegrationAdapter` protocol, normalizing their API payloads into canonical `Device` schema. Adapters handle:

- Parsing vendor API responses
- Mapping to DeviceType enum
- Device control commands

### Repository Pattern (Data Access)

Repositories abstract database access. Examples:

- `property/repository/` — Device CRUD
- `identity/repository/` — User queries

### Service Layer

Services encapsulate business logic:

- Orchestrate repositories
- Validate domain rules
- Handle inter-module communication

### Domain-Driven Design

Core domain in `property/domain/`:

- `Device` — Unified device schema across all vendors
- `DeviceType` — Enum of supported device types (lock, thermostat, camera, etc)
- `raw_state` dict — Vendor-specific metadata stored alongside canonical fields

## API Structure

Routes are included in main.py from:

- `demo.routes` — Development endpoints
- `identity.api.routes` — Auth endpoints
- `intelligence.api.routes` — AI device control
- `property.api.routes` — Property/device endpoints (includes all integration routers)

## Database

PostgreSQL with SQLAlchemy ORM. Migrations via Alembic.

**Related:** `backend/src/db/README.md`

## Configuration

Settings from environment variables. See `config.py` for available options.

## Testing

Run all tests:

```bash
cd backend && python -m pytest
```

Run specific module:

```bash
python -m pytest src/property/
```

## Key Concepts

### Unified Device Schema

All devices from any vendor (August, Bluetooth, Govee, etc) are normalized to a single `Device` model with:

- Canonical fields: `device_type`, `vendor`, `vendor_specific_id`, etc.
- `raw_state` dict for vendor-specific metadata
- No separate per-vendor device schemas for storage

### Organization Isolation

All resources belong to an `organization_id`. Queries automatically filter by organization (Row-Level Security in DB).

### Tool Use for Device Control

Natural language commands like "turn on the living room light" are parsed via Claude tool use, then executed through `intelligence.executor`.

## Related Documentation

- [Property Module](property/README.md) — Device management
- [Integrations](integrations/README.md) — Vendor adapters
- [Intelligence](intelligence/README.md) — AI device control
- [Identity](identity/README.md) — Auth & users
- [Shared](shared/README.md) — DB & utilities
