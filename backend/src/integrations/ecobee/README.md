# Ecobee Thermostats Integration (Backend)

REST API endpoints for managing Ecobee smart thermostats.

## Overview

Ecobee integration for smart thermostat control. Sync thermostats, monitor temperature, set target temps, and manage schedules.

## Endpoints

### GET /integrations/ecobee/thermostats

List all Ecobee thermostats for an organization or property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property
- `organization_id` (UUID): Required for organization-wide query

**Response:** 200 OK

```json
[
  {
    "id": "thermostat-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "ecobee_id": "ecobee_123456",
    "name": "Main Floor",
    "model": "Ecobee SmartThermostat with Voice Control",
    "current_temp": 72,
    "target_temp": 70,
    "mode": "heat",
    "humidity": 45,
    "online": true,
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/ecobee/thermostats

Add an Ecobee thermostat to a property.

**Request:**

```json
{
  "ecobee_id": "ecobee_123456",
  "name": "Main Floor",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** 201 Created

```json
{
  "id": "thermostat-uuid",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "ecobee_id": "ecobee_123456",
  "name": "Main Floor",
  "current_temp": 72,
  "target_temp": 70,
  "mode": "heat",
  "online": true,
  "last_sync": "2026-06-24T14:30:00Z",
  "created_at": "2026-06-24T14:30:00Z"
}
```

### POST /integrations/ecobee/thermostats/{thermostat_id}/temperature

Set target temperature.

**Request:**

```json
{
  "target_temp": 72
}
```

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Main Floor target temperature set to 72°F",
  "thermostat_id": "thermostat-uuid",
  "target_temp": 72
}
```

### POST /integrations/ecobee/thermostats/{thermostat_id}/mode

Set thermostat mode (heat, cool, auto, off).

**Request:**

```json
{
  "mode": "heat"
}
```

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Main Floor mode set to heat",
  "mode": "heat"
}
```

## Files

| File                   | Purpose                             |
| ---------------------- | ----------------------------------- |
| `adapter.py`           | EcobeeAdapter implementing protocol |
| `domain.py`            | EcobeeThermostat Pydantic model     |
| `models.py`            | EcobeeModel SQLAlchemy ORM          |
| `schemas.py`           | Request/response DTOs               |
| `routes.py`            | FastAPI router with endpoints       |
| `tests/test_ecobee.py` | Test cases for all flows            |
| `README.md`            | This file                           |

## Types

### EcobeeThermostat (domain.py)

```python
class EcobeeThermostat(BaseModel):
    id: UUID
    property_id: UUID
    integration_id: UUID
    ecobee_id: str              # Unique to Ecobee
    name: str
    model: str
    current_temp: float
    target_temp: float
    mode: Literal["heat", "cool", "auto", "off"]
    humidity: int               # 0-100
    online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
```

## Testing

Run tests:

```bash
cd backend && python -m pytest src/integrations/ecobee/
```

Test coverage includes:

- Adding thermostat
- Temperature control
- Mode changes
- List thermostats with filtering
- Online status tracking

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
