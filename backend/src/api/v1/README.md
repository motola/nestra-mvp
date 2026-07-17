# API v1

Version 1 of AlphaCon API.

## Overview

Currently all v1 routes are defined inline in module-specific files:

- `property/api/routes.py` — Device endpoints
- `identity/api/routes.py` — Auth endpoints
- `intelligence/api/routes.py` — AI device control
- `demo/routes.py` — Demo endpoints

## Routing

All routers are included in `main.py` at root level (no `/api/v1/` prefix):

```python
# main.py
app.include_router(property_router)
app.include_router(identity_router)
app.include_router(intelligence_router)
app.include_router(demo_router)
```

This directory is a placeholder for future versioning.

## Future: Multi-Version API

When API v2 is needed:

1. Create `/api/v2/` directory with versioned routes
2. Keep v1 routes here for backwards compatibility
3. Mount both versions with different prefixes:

```python
# main.py
from api.v1.routes import router as v1_router
from api.v2.routes import router as v2_router

app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

## Related

- API layer: `backend/src/api/README.md`
- Backend overview: `backend/src/README.md`
