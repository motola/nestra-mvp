# Identity Services

Business logic for authentication and user/organization management.

## Pattern

Services encapsulate auth logic and inter-module workflows:

```
HTTP Request
    ↓
Service (auth logic, validation)
    ↓
Repository (data access)
    ↓
Database
```

## Key Services (Planned)

### AuthService

```python
class AuthService:
    async def register(email: str, password: str, display_name: str) -> (User, token)
        # 1. Validate email not taken
        # 2. Hash password
        # 3. Create user via repository
        # 4. Generate JWT token
        # 5. Return user + token

    async def login(email: str, password: str) -> (User, token)
        # 1. Look up user by email
        # 2. Validate password
        # 3. Generate JWT token
        # 4. Return user + token

    async def decode_token(token: str) -> User | None
        # Verify JWT signature
        # Return user or None if invalid
```

### UserService

```python
class UserService:
    async def get_user(user_id: UUID, org_id: UUID) -> User
        # Only return user if they belong to org_id (multi-tenant)

    async def list_users(org_id: UUID) -> list[User]
        # Only return users in org_id

    async def update_user(user_id: UUID, display_name: str, role: UserRole) -> User
        # Update user info (admin only)

    async def delete_user(user_id: UUID) -> bool
        # Delete user (admin only)
```

### OrganizationService

```python
class OrganizationService:
    async def create_org(name: str, creator_id: UUID) -> Organization
        # Create new org
        # Add creator as admin

    async def list_user_orgs(user_id: UUID) -> list[Organization]
        # Return all orgs user belongs to
```

## Authorization

Services check roles before allowing operations:

```python
async def update_user(self, user: User, target_id: UUID, new_role: UserRole):
    # Only admins can change roles
    if user.role != UserRole.ADMIN:
        raise PermissionError("Only admins can update roles")

    # Find target user in same org
    target = await self.user_repo.get_by_id(target_id)
    if target.organization_id != user.organization_id:
        raise PermissionError("Cannot modify users from other orgs")

    # Update
    target.role = new_role
    return await self.user_repo.update(target)
```

## Related

- Identity module: `backend/src/identity/README.md`
- Domain models: `backend/src/identity/domain/README.md`
- Repository (data access): `backend/src/identity/repository/README.md`
- API endpoints (call services): `backend/src/identity/api/README.md`
