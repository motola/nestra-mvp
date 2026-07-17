# Property Services

Business logic layer — orchestrates repositories, validates domain rules, coordinates between modules.

## Pattern

Services encapsulate domain logic and inter-module workflows:

```
HTTP Request
    ↓
Service (business logic)
    ↓
Repository (data access)
    ↓
Database
```

## Key Services (Planned)

### DeviceService

```python
class DeviceService:
    async def list_devices_for_property(property_id: UUID) -> list[Device]
    async def get_device(device_id: UUID) -> Device
    async def sync_devices(property_id: UUID, integration_id: UUID) -> list[Device]
        # 1. Call integration adapter to fetch from vendor
        # 2. Normalize to Device schema
        # 3. Persist via repository
    async def execute_command(device_id: UUID, command: str, params: dict) -> bool
        # 1. Load device from repository
        # 2. Call integration adapter execute()
        # 3. Update device state
```

### Device Sync Pipeline

Orchestrates full sync workflow:

1. Call integration adapter `fetch_devices()`
2. Normalize vendor payloads to Device schema
3. Upsert devices via repository
4. Track sync timestamp
5. Return synced devices

## Related

- Property module: `backend/src/property/README.md`
- Repository (data access): `backend/src/property/repository/README.md`
- API endpoints (call services): `backend/src/property/api/README.md`
- Integrations (adapters called by services): `backend/src/integrations/README.md`
- Intelligence (queries devices from services): `backend/src/intelligence/README.md`
