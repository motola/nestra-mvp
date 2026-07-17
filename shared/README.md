# Shared Infrastructure

Shared utilities, clients, and models used across all services (backend, intelligence).

## Structure

```
shared/
├── README.md (this file)
├── clients/
│   ├── __init__.py
│   ├── http_client.py      # Agnostic HTTP client for all APIs
│   ├── claude_client.py    # Claude-specific client
│   └── README.md
└── db.py                   # Database configuration (will be moved here)
```

## API Clients

### HttpClient

Generic HTTP client for all third-party vendor APIs.

**Usage:**

```python
from shared.clients import HttpClient

client = HttpClient(timeout=30, max_retries=3)
response = await client.post(
    "https://api.august.com/devices",
    headers={"Authorization": f"Bearer {api_key}"},
)
```

Used by:

- Device integrations (August, Bluetooth, TP-Link, etc)
- Any service making HTTP calls

### ClaudeClient

Wrapper around Anthropic SDK for Claude API.

**Usage:**

```python
from shared.clients import ClaudeClient

client = ClaudeClient(api_key=api_key)
response = await client.create_message(
    messages=[{"role": "user", "content": "turn on light"}],
    system="You control smart home devices",
    tools=[...],
)
```

Used by:

- Intelligence service

## Database Configuration

Shared SQLAlchemy setup in `db.py`:

```python
from shared.db import Base, SessionLocal, engine
```

## Multi-Service Architecture

Services communicate via HTTP (OpenAPI contracts):

```
Backend                Intelligence Service
    (main.py)              (src/main.py)
        |                       |
        +-------HTTP API--------+
        |                       |
    [routes]              [intelligence/api/routes.py]
        |                       |
    [services]            [services.py]
        |                       |
    [integrations]         [executor.py]
        |                       |
        +---- Shared DB --------+
```

## Adding Shared Utilities

Guidelines:

1. **Cross-service code only** — If used by 2+ services, move to shared
2. **Minimize coupling** — Don't import service-specific code into shared
3. **Version carefully** — Shared changes affect multiple services
4. **Document thoroughly** — READMEs in each shared submodule

Examples of shared code:

- API clients (HttpClient, ClaudeClient)
- Database setup (db.py)
- Common domain models (future)
- Configuration helpers (future)

Non-shared (service-specific):

- Backend integrations
- Intelligence services
- Backend utility modules → `backend/src/utility/`
- Intelligence utility modules → `intelligence/src/utility/`

## Related

- Backend: `../backend/README.md`
- Intelligence: `../intelligence/README.md`
- Shared Clients: `clients/README.md`
