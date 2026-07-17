# Identity Module

User and organization management, authentication, and authorization.

## Overview

Manages:

- Users — Individual accounts
- Organizations — Tenants (multi-tenant support)
- Authentication — Login, session management
- Authorization — Role-based access control (RBAC)

## Structure

```
identity/
├── README.md (this file)
├── domain/
│   └── __init__.py      # User, Organization domain models
├── api/
│   └── routes.py        # FastAPI auth endpoints
├── repository/
│   └── models.py        # ORM models
└── services/
    └── __init__.py      # Auth business logic
```

## Domain Models

### User

```python
class User(BaseModel):
    id: UUID
    email: str
    display_name: str
    organization_id: UUID  # Multi-tenant: belongs to org
    role: UserRole         # admin, editor, viewer
    created_at: datetime
    updated_at: datetime
```

### Organization

```python
class Organization(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
```

### UserRole (StrEnum)

```python
class UserRole(StrEnum):
    ADMIN = "admin"       # Full access
    EDITOR = "editor"     # Modify devices
    VIEWER = "viewer"     # Read-only
```

## API Routes

- `POST /auth/register` — Create account
- `POST /auth/login` — Login
- `POST /auth/logout` — Logout
- `GET /users/me` — Current user info
- `GET /organizations` — List orgs (admin)

## Multi-Tenant Architecture

Users belong to organizations. All queries include `organization_id` filter:

```python
async def get_user(user_id: UUID, org_id: UUID) -> User:
    # Only returns user if they belong to org_id
    return await self.db.query(UserModel).filter(
        UserModel.id == user_id,
        UserModel.organization_id == org_id,
    ).first()
```

This prevents cross-tenant data leakage.

## Authorization

Middleware checks user role before allowing actions:

```python
@router.delete("/devices/{id}")
async def delete_device(id: UUID, user: User = Depends(get_current_user)):
    # Only editors and admins can delete
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Forbidden")
```

## Related

- Backend overview: `backend/src/README.md`
- Property module (organization isolation): `backend/src/property/README.md`
- Main app (middleware): `backend/src/main.py`
