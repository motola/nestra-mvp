# Identity API

FastAPI endpoints for authentication and user/organization management.

## Routes

### Authentication

- `POST /auth/register` — Create account
  - Body: `{email, password, display_name}`
  - Returns: `{user, token}`

- `POST /auth/login` — Login
  - Body: `{email, password}`
  - Returns: `{user, token}`

- `POST /auth/logout` — Logout
  - Invalidates session/token

### Users

- `GET /users/me` — Current user info
  - Returns: `{id, email, display_name, organization_id, role}`

- `GET /users` — List users in organization (admin only)
  - Returns: `[{id, email, display_name, role}]`

- `PATCH /users/{id}` — Update user (admin only)
  - Body: `{display_name?, role?}`

- `DELETE /users/{id}` — Delete user (admin only)

### Organizations

- `GET /organizations` — List user's organizations
  - Returns: `[{id, name, created_at}]`

- `POST /organizations` — Create organization
  - Body: `{name}`
  - Returns: `{id, name}`

## Middleware

Global middleware in `main.py` extracts user from JWT token and injects into request context:

```python
@app.middleware("http")
async def add_user_context(request: Request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await decode_token(token)  # or None
    request.state.user = user
    return await call_next(request)
```

Endpoints use `Depends(get_current_user)` to access:

```python
@router.get("/users/me")
async def get_me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(**user.model_dump())
```

## Related

- Identity module: `backend/src/identity/README.md`
- Domain models: `backend/src/identity/domain/README.md`
- Services (auth logic): `backend/src/identity/services/README.md`
- Main app (middleware): `backend/src/main.py`
