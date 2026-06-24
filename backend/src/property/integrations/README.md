# Property Integrations

REST API endpoints for all vendor integrations (Bluetooth, Govee, Lifx, Nest, etc).

## Overview

Each integration is self-contained with its own:
- **Domain model** — Pydantic class for the core entity
- **ORM model** — SQLAlchemy table mapping
- **Schemas** — Request/response DTOs
- **Routes** — FastAPI endpoints
- **Tests** — Unit and integration test suite

## Architecture

```
property/integrations/
├── README.md (this file)
├── base.py (base integration interface)
├── bluetooth/
│   ├── README.md
│   ├── domain.py (BluetoothDevice model)
│   ├── models.py (BluetoothDeviceModel ORM)
│   ├── schemas.py (DTOs)
│   ├── routes.py (endpoints)
│   └── tests/test_bluetooth.py
├── govee/ (future)
│   ├── domain.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── tests/test_govee.py
└── lifx/ (future)
    ├── ...
```

## Base Integration Interface

`base.py` defines the contract all integrations must follow:

```python
class Integration(ABC):
    vendor_name: str

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def discover_devices(self) -> list[dict[str, Any]]:
        pass
```

Integrations can implement additional methods as needed.

## Adding a New Integration

### 1. Create folder structure

```bash
mkdir -p src/property/integrations/[vendor]/{tests}
touch src/property/integrations/[vendor]/{__init__,domain,models,schemas,routes}.py
touch src/property/integrations/[vendor]/tests/{__init__,test_[vendor]}.py
touch src/property/integrations/[vendor]/README.md
```

### 2. Define domain model (domain.py)

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class GoveeDevice(BaseModel):
    id: UUID
    property_id: UUID
    integration_id: UUID
    device_id: str  # Govee API device ID
    name: str
    device_type: str  # "light", "plug", etc
    is_online: bool
    brightness: int  # 0-100
    color_temp: int | None  # Kelvin
    last_sync: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        frozen = True
```

### 3. Define ORM model (models.py)

```python
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base

class GoveeDeviceModel(Base):
    __tablename__ = "govee_devices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("portfolios.id"))
    integration_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integrations.id"))
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    brightness: Mapped[int] = mapped_column(Integer, default=0)
    color_temp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("property_id", "device_id", name="uq_device_property_govee"),
    )
```

### 4. Define schemas (schemas.py)

```python
from pydantic import BaseModel, Field
from uuid import UUID

class GoveeDeviceIn(BaseModel):
    device_id: str = Field(..., description="Govee API device ID")
    name: str
    property_id: UUID
    device_type: str = Field(default="unknown")
    brightness: int = Field(default=0, ge=0, le=100)
    color_temp: int | None = None

class GoveeDeviceOut(BaseModel):
    id: UUID
    device_id: str
    name: str
    device_type: str
    is_online: bool
    brightness: int
    color_temp: int | None
    last_sync: datetime
    created_at: datetime
```

### 5. Define routes (routes.py)

```python
from fastapi import APIRouter, HTTPException, status
from dependencies import SettingsDep
from property.integrations.govee.schemas import GoveeDeviceIn, GoveeDeviceOut

router = APIRouter(prefix="/integrations/govee", tags=["property"])

@router.post("/devices", response_model=GoveeDeviceOut, status_code=status.HTTP_201_CREATED)
async def add_device(body: GoveeDeviceIn, settings: SettingsDep) -> GoveeDeviceOut:
    """Add a Govee device to property."""
    # Implementation
    pass

@router.get("/devices", response_model=list[GoveeDeviceOut])
async def list_devices(property_id: UUID | None = None, settings: SettingsDep | None = None):
    """List Govee devices."""
    # Implementation
    pass
```

### 6. Write tests (tests/test_govee.py)

```python
import unittest
from uuid import uuid4
from config import get_settings

class TestGoveeDevices(unittest.TestCase):
    def setUp(self):
        self.settings = get_settings()

    def test_add_device_success(self):
        # Test implementation
        pass
```

### 7. Register in main API (property/api/routes.py)

```python
from property.integrations.govee import router as govee_router

router = APIRouter()
router.include_router(govee_router)
```

### 8. Update test runner (backend/run_tests.py)

```python
from property.integrations.govee.tests import test_govee

suite.addTests(loader.loadTestsFromModule(test_govee))
```

## Endpoint Patterns

All integrations follow REST conventions:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/integrations/[vendor]/devices` | Add/discover device |
| GET | `/integrations/[vendor]/devices` | List devices (filtered by property) |
| DELETE | `/integrations/[vendor]/devices/{id}` | Remove device |
| PATCH | `/integrations/[vendor]/devices/{id}` | Update device state |

## Multi-Tenancy & RLS

**Important:** All queries must filter by `organization_id` via Row-Level Security policies.

In Postgres:
```sql
CREATE POLICY rls_govee_devices ON govee_devices
FOR SELECT USING (
  property_id IN (
    SELECT id FROM portfolios WHERE organization_id = current_setting('app.org_id')
  )
);
```

In code (future — currently using mock storage):
```python
# Backend will enforce RLS at query time
devices = db.query(GoveeDeviceModel).filter(
    GoveeDeviceModel.organization_id == current_user.organization_id
).all()
```

## Testing Strategy

Each integration should have:
- **Unit tests** for individual functions
- **Integration tests** for full workflows
- **Mock storage** for MVP
- **Database tests** (after RLS is wired)

Run all tests:
```bash
cd backend && python run_tests.py
```

Run single integration:
```bash
python -m unittest property.integrations.bluetooth.tests.test_bluetooth -v
```

## Shared Patterns

### Timestamps

Every device model has:
- `created_at` — When device was first added
- `updated_at` — When device was last modified
- `last_sync` — When device was last synced from vendor API

### Status Codes

- `201 Created` — Device successfully added/created
- `200 OK` — Successful GET/PATCH/DELETE
- `400 Bad Request` — Invalid request data
- `404 Not Found` — Device or property doesn't exist
- `409 Conflict` — Duplicate device or business logic violation

### Error Handling

Use HTTPException with proper status codes:
```python
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Device already paired to this property"
)
```

## Future Enhancements

- **Vendor API integration** — Call real Govee/Lifx/Nest APIs
- **Rate limiting** — Throttle API calls per tenant
- **Background sync** — Periodic device state polling
- **WebSocket updates** — Real-time state changes pushed to frontend
- **Device control** — Brightness, color, temperature endpoints
- **Automation triggers** — Devices as automation conditions/actions
- **Cost tracking** — Energy usage per device/property

## Related

- Frontend: `frontend/src/integrations/`
- Bluetooth details: `property/integrations/bluetooth/README.md`
- Property API router: `property/api/routes.py`
