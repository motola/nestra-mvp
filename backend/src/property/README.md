# Property Module

Manages properties and devices — the core domain for smart home management. Normalizes all vendor-specific device APIs into a unified schema.

## Overview

Properties represent physical buildings/homes. Devices are smart home devices (locks, thermostats, cameras, etc) associated with properties. All devices from any vendor (August, Bluetooth, Govee, etc) are normalized to a single canonical Device schema.

## Structure

```
property/
├── README.md (this file)
├── domain/
│   └── __init__.py      # Device, DeviceType domain models
├── api/
│   └── routes.py        # FastAPI router (device endpoints + integration routers)
├── persistence/
│   └── device_repository.py  # Database models
├── repository/
│   └── models.py        # ORM models
└── services/
    └── __init__.py      # Business logic
```

## Domain Model

### Device (property/domain/**init**.py)

Unified smart home device across all integrations. Single schema — no per-vendor variants.

```python
class Device(BaseModel):
    """Unified smart home device."""
    id: UUID | None
    organization_id: UUID
    property_id: UUID
    integration_id: UUID
    device_type: DeviceType        # lock, thermostat, camera, etc
    vendor: str                    # "august", "bluetooth", "govee", etc
    vendor_specific_id: str        # vendor's device ID
    vendor_name: str | None        # friendly name from vendor
    online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
    raw_state: dict[str, object]   # vendor-specific metadata
```

### DeviceType (StrEnum)

```python
class DeviceType(StrEnum):
    LOCK = "lock"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    PLUG = "plug"
    SENSOR = "sensor"
    SPEAKER = "speaker"
```

## API Routes

Currently mounted at `/` (no `/properties/` prefix). Includes all integration routers:

- August Smart Locks: `/integrations/august/*`
- Bluetooth devices: `/integrations/bluetooth/*`
- Device sync & state: Future endpoints in `services/`

**Related:** `integrations/august/README.md`, `integrations/bluetooth/README.md`

## Design Patterns

### Single Unified Schema

No `DeviceLock`, `DeviceCamera`, `DeviceThermo` — one `Device` for all. Vendor differences stored in `raw_state` dict.

**Why:** Reduces code duplication, simplifies inventory APIs, normalizes control across vendors.

### Repository Pattern

`property/repository/` encapsulates database access:

- Device CRUD
- Query by property, organization, device_type
- Filtering, pagination

### Adapter-to-Device Pipeline

1. Integration adapter fetches from vendor API
2. Adapter calls `create_device_data()` to build Device
3. Repository persists Device
4. Intelligence layer queries repository for control

## Adding a New Device Type

1. Add enum value to `DeviceType` in `property/domain/__init__.py`
2. Create new integration in `integrations/[vendor]/`
3. Implement `IntegrationAdapter` protocol
4. Repository queries will automatically filter by new type

## Adding a New Integration

1. Create `integrations/[vendor]/` directory
2. Implement `IntegrationAdapter` protocol in adapter.py:
   - `fetch_devices()` — fetch from vendor API, return Device list
   - `fetch_state()` — update device state
   - `execute()` — send control commands
3. Normalize vendor payloads → Device schema
4. Store vendor-specific data in `raw_state` dict
5. Register router in `property/api/routes.py`

Example:

```python
# integrations/govee/adapter.py
class GoveeAdapter(IntegrationAdapter):
    vendor = "govee"

    async def fetch_devices(self, *, organization_id, property_id, integration_id):
        # Call Govee API
        govee_devices = await self.govee_client.get_devices()

        # Convert to canonical Device schema
        devices = []
        for gd in govee_devices:
            device = Device(
                id=None,  # repository will assign
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                device_type=self._map_govee_type(gd.type),
                vendor="govee",
                vendor_specific_id=gd.device_id,
                vendor_name=gd.name,
                online=gd.online,
                last_sync=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                raw_state={"govee_type": gd.type, "govee_model": gd.model},
            )
            devices.append(device)
        return devices
```

## Testing

Tests in `tests/` (to be created). Coverage:

- Device creation & retrieval
- Filtering by property, organization, device_type
- Repository persistence
- Service business logic

## Related

- Backend overview: `backend/src/README.md`
- Integrations: `backend/src/integrations/README.md`
- Intelligence (device control): `backend/src/intelligence/README.md`
- Identity (org/user context): `backend/src/identity/README.md`
