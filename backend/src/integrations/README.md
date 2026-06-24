# Integrations Module

Vendor integrations (Bluetooth, Govee, Lifx, Nest, etc). Cross-cutting concern used by property, intelligence, automations, and devices contexts.

## Structure

```
integrations/
├── README.md (this file)
├── __init__.py
├── base.py (base integration interface)
├── models.py (shared IntegrationModel ORM)
├── bluetooth/
│   ├── README.md
│   ├── __init__.py
│   ├── domain.py (BluetoothDevice model)
│   ├── models.py (BluetoothDeviceModel ORM)
│   ├── schemas.py (request/response DTOs)
│   ├── routes.py (endpoints)
│   └── tests/test_bluetooth.py
├── govee/ (future)
└── lifx/ (future)
```

## Adding a New Integration

1. Create `integrations/[vendor]/` folder
2. Define domain model in `domain.py`
3. Define ORM model in `models.py`
4. Define schemas in `schemas.py`
5. Define routes in `routes.py`
6. Write tests in `tests/test_[vendor].py`
7. Create `README.md`
8. Register router in `property/api/routes.py`

## Usage

Each context imports from integrations as needed:

```python
from integrations.bluetooth import router as bluetooth_router
from integrations.models import IntegrationModel
```

## Related

- Backend property context: `backend/src/property/`
- Frontend integrations: `frontend/src/integrations/`
