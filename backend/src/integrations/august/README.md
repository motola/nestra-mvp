# August Smart Lock Integration (Backend)

REST API endpoints for managing August Smart Locks on properties.

## Overview

Keyless access management for properties. Add locks, control lock/unlock state, monitor battery levels, and audit access.

## Endpoints

### POST /integrations/august/locks

Add an August Smart Lock to a property.

**Request:**

```json
{
  "lock_id": "august_abc123",
  "name": "Front Door",
  "location": "Building A, Unit 101",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "battery_level": 95,
  "is_locked": true,
  "model": "August Pro"
}
```

**Response:** 201 Created

```json
{
  "id": "lock-uuid",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "lock_id": "august_abc123",
  "name": "Front Door",
  "location": "Building A, Unit 101",
  "battery_level": 95,
  "is_locked": true,
  "is_online": true,
  "model": "August Pro",
  "last_sync": "2026-06-24T14:30:00Z",
  "created_at": "2026-06-24T14:30:00Z"
}
```

### GET /integrations/august/locks

List locks, optionally filtered by property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "lock-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "lock_id": "august_abc123",
    "name": "Front Door",
    "battery_level": 95,
    "is_locked": true,
    "is_online": true,
    "model": "August Pro",
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/august/locks/{lock_id}/lock

Lock a device.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Lock 'Front Door' is now locked"
}
```

### POST /integrations/august/locks/{lock_id}/unlock

Unlock a device.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Lock 'Front Door' is now unlocked"
}
```

### DELETE /integrations/august/locks/{lock_id}

Remove a lock.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Lock 'Front Door' removed"
}
```

## Testing

Run tests:

```bash
cd backend && python run_tests.py
```

**Test Coverage:** 6 comprehensive tests

- Add lock (success + duplicate rejection)
- Lock/unlock operations
- List locks with filtering
- Remove lock

## Related

- Integrations: `backend/src/integrations/`
- Property API: `backend/src/property/api/routes.py`
