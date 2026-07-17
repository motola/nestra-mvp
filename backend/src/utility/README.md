# Utility Module

Backend-internal utilities and common infrastructure shared across backend modules.

## Structure

```
utility/
├── README.md (this file)
└── db.py       # Database configuration & Base
```

## db.py

SQLAlchemy setup shared by all ORM models.

### Base

Pydantic BaseModel used by all domain models:

```python
from pydantic import BaseModel

class Base(BaseModel):
    """Shared Pydantic base for domain models."""
    model_config = ConfigDict(from_attributes=True)
```

### SQLAlchemy Base

Declarative base for ORM models:

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

All ORM models inherit from this:

```python
class DeviceModel(Base):
    __tablename__ = "devices"
    # ...
```

### Session Management

Database session factory:

```python
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Common Models (Future)

Plan to add shared models:

- `BaseEntity` — id, created_at, updated_at timestamps
- `TimestampMixin` — created_at, updated_at
- `AuditMixin` — Track who created/modified (created_by, updated_by)

## Related

- Backend overview: `backend/src/README.md`
- Database: `backend/src/db/README.md`
- Property persistence (uses Base): `backend/src/property/persistence/README.md`
- Identity repository (uses Base): `backend/src/identity/repository/README.md`
