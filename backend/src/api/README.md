# API Layer

HTTP routing and versioning structure.

## Structure

```
api/
├── README.md (this file)
└── v1/       # API version 1 (currently empty, routes defined inline)
```

## Current Architecture

API v1 routes are currently defined inline in module-specific files:

- `property/api/routes.py` — Property/device endpoints
- `identity/api/routes.py` — Auth endpoints
- `intelligence/api/routes.py` — AI device control endpoints
- `demo/routes.py` — Development endpoints

All routers are included in `main.py`:

```python
app.include_router(demo_router)
app.include_router(identity_router)
app.include_router(intelligence_router)
app.include_router(property_router)
```

## Future: API Versioning

When major breaking changes require a new API version:

1. Create `api/v2/` directory
2. Move routers to `v2/` subdirectories
3. Keep `api/v1/` for backwards compatibility
4. Mount both versions in `main.py`:

```python
app.include_router(property_v1_router, prefix="/api/v1")
app.include_router(property_v2_router, prefix="/api/v2")
```

## Response Format

All endpoints follow consistent response format:

**Success (200):**

```json
{
  "status": "success",
  "data": { ... }
}
```

**Error (400+):**

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

## Related

- Backend overview: `backend/src/README.md`
- Property API: `backend/src/property/api/README.md`
- Identity API: `backend/src/identity/api/README.md`
- Intelligence API: `backend/src/intelligence/api/README.md`
- Demo routes: `backend/src/demo/README.md`
