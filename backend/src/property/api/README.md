# Property API

FastAPI HTTP endpoints for managing properties and devices.

## Routes

Router is mounted at root (`/`) and includes all integration routers:

### Integration Routes (Auto-included)

- August Smart Locks: `/integrations/august/*`
  - `POST /integrations/august/locks` — Add lock
  - `GET /integrations/august/locks` — List locks
  - `POST /integrations/august/locks/{id}/lock` — Lock device
  - `POST /integrations/august/locks/{id}/unlock` — Unlock device

- Bluetooth devices: `/integrations/bluetooth/*`
  - `POST /integrations/bluetooth/pair` — Pair device
  - `GET /integrations/bluetooth/devices` — List devices
  - `POST /integrations/bluetooth/unpair` — Unpair device

### Future Routes

- Device sync pipeline
- Device state queries
- Batch device operations

## Structure

```
property/api/
├── routes.py  # FastAPI router, includes all integration routers
└── (schemas, endpoints to be added)
```

## Adding Endpoints

1. Create `property/api/schemas.py` for request/response DTOs
2. Add endpoint handlers in `property/api/routes.py`
3. Import services from `property/services/`
4. Return schema-validated responses

Example:

```python
# routes.py
from fastapi import APIRouter, Depends
from property.services import get_device_service
from property.api.schemas import DeviceOut

router = APIRouter()

@router.get("/devices")
async def list_devices(
    property_id: UUID,
    service: DeviceService = Depends(get_device_service),
) -> list[DeviceOut]:
    devices = await service.list_devices_for_property(property_id)
    return [DeviceOut(**d.model_dump()) for d in devices]
```

## Related

- Property module: `backend/src/property/README.md`
- Integrations: `backend/src/integrations/README.md`
- Services: `backend/src/property/services/README.md`
- Repository: `backend/src/property/repository/README.md`
