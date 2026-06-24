# Bluetooth Integration (Backend)

FastAPI endpoints for device pairing, unpairing, and listing via Web Bluetooth API.

## Overview

REST API for managing Bluetooth device lifecycle: pairing newly discovered devices, maintaining a registry, and filtering by property. Uses mock in-memory storage (MVP) — will be replaced with database queries in production.

## Endpoints

### POST /integrations/bluetooth/pair

Pair a newly discovered Bluetooth device to a property.

**Request:**

```json
{
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "name": "Living Room Light",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "device_type": "light",
  "rssi": -45,
  "battery_level": 85
}
```

**Response:** 201 Created

```json
{
  "device_id": "d94cab91-6e79-48e4-abc4-bd0206512024",
  "status": "paired",
  "message": "Device paired successfully"
}
```

**Errors:**

- `409 Conflict` — Device with same MAC already paired

---

### POST /integrations/bluetooth/unpair

Remove a paired Bluetooth device.

**Query Parameters:**

- `device_id` (UUID): The device to unpair

**Response:** 200 OK

```json
{
  "status": "unpaired",
  "message": "Device unpaired successfully"
}
```

**Errors:**

- `404 Not Found` — Device does not exist

---

### GET /integrations/bluetooth/devices

List paired Bluetooth devices, optionally filtered by property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "d94cab91-6e79-48e4-abc4-bd0206512024",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "name": "Living Room Light",
    "device_type": "light",
    "rssi": -45,
    "battery_level": 85,
    "is_paired": true,
    "last_sync": "2026-06-23T22:54:15.122625Z",
    "created_at": "2026-06-23T22:54:15.122627Z"
  }
]
```

## Files

| File                      | Purpose                             |
| ------------------------- | ----------------------------------- |
| `domain.py`               | BluetoothDevice Pydantic model      |
| `models.py`               | BluetoothDeviceModel SQLAlchemy ORM |
| `schemas.py`              | Request/response DTOs               |
| `routes.py`               | FastAPI router with 3 endpoints     |
| `tests/test_bluetooth.py` | 8 test cases covering all flows     |
| `README.md`               | This file                           |

## Types

### BluetoothDevice (domain.py)

```python
class BluetoothDevice(BaseModel):
    id: UUID
    property_id: UUID
    integration_id: UUID
    mac_address: str  # unique per organization
    name: str  # friendly name from Web Bluetooth API
    device_type: str  # "light", "sensor", etc
    rssi: int  # signal strength in dBm
    battery_level: int | None  # 0-100
    is_paired: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
```

### BluetoothDeviceModel (models.py)

SQLAlchemy ORM mapping to `bluetooth_devices` table:

- Unique constraint on `(property_id, mac_address)` — no duplicate MACs per property
- Foreign keys to `portfolios` (property) and `integrations`

### Schemas (schemas.py)

```python
class BluetoothDeviceIn(BaseModel):
    mac_address: str
    name: str
    property_id: UUID
    device_type: str = "unknown"
    rssi: int = -100
    battery_level: int | None = None

class BluetoothDeviceOut(BaseModel):
    id: UUID
    property_id: UUID
    mac_address: str
    name: str
    device_type: str
    rssi: int
    battery_level: int | None
    is_paired: bool
    last_sync: datetime
    created_at: datetime
```

## Testing

**Test Coverage:** 8 comprehensive tests in `tests/test_bluetooth.py`

| Test                                    | What                                  |
| --------------------------------------- | ------------------------------------- |
| `test_pair_device_success`              | Pair a new device successfully        |
| `test_pair_duplicate_device_fails`      | Reject duplicate MAC addresses (409)  |
| `test_unpair_device_success`            | Unpair a device successfully          |
| `test_unpair_nonexistent_device_fails`  | Reject unpair of missing device (404) |
| `test_list_devices_empty`               | List returns empty array initially    |
| `test_list_devices_filters_by_property` | Filtering by property_id works        |
| `test_paired_device_has_valid_data`     | All fields preserved after pairing    |
| `test_full_pairing_workflow`            | Complete: pair → list → unpair flow   |

Run tests:

```bash
cd backend && python run_tests.py
```

## Implementation Details

### Mock Storage (MVP)

Currently uses in-memory dictionaries:

```python
_MOCK_DEVICES: dict[UUID, BluetoothDeviceOut] = {}
_MOCK_INTEGRATIONS: dict[str, UUID] = {}
```

**Transition to DB:**

1. Create Alembic migration to create `bluetooth_devices` table
2. Replace `_MOCK_DEVICES` dict with SQLAlchemy queries
3. Use `BluetoothDeviceModel` for ORM operations
4. Add RLS policies for `organization_id` filtering

### Uniqueness Constraint

MAC addresses must be unique **per property** (not globally):

```python
UniqueConstraint("property_id", "mac_address", name="uq_device_property_mac")
```

This allows same MAC in different properties (e.g., two Bluetooth lights in two buildings).

### Timestamps

- `created_at` — When device was first paired
- `updated_at` — When device was last modified
- `last_sync` — When device was last discovered/synced

### Status Codes

- `201 Created` — Device paired successfully
- `200 OK` — Unpair success, device list returned
- `404 Not Found` — Device does not exist
- `409 Conflict` — Duplicate MAC or business logic conflict

## Future Work

- **Real Database:** Replace mock storage with Postgres queries
- **Device Control:** Read/write Bluetooth characteristics (brightness, color, etc)
- **Polling/Sync:** Periodic device state refresh via background job
- **Battery Alerts:** Notify when device battery is low
- **WebSocket Updates:** Real-time device state changes pushed to frontend
- **Pairing Timeout:** Auto-unpair devices not seen in 30 days

## Related

- Frontend: `frontend/src/integrations/bluetooth/`
- Integrations Overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Base Integration: `backend/src/integrations/base.py`
