# Authentication API Reference

Base path: `/api/v1/auth`

## Endpoints

### POST /auth/login

Authenticate a user and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` — Invalid credentials
- `403` — Account locked (too many failed attempts)
- `403` — Account inactive

### POST /auth/register

Create a new user account.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "Jane Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### POST /auth/refresh

Exchange a refresh token for new access and refresh tokens.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### POST /auth/logout

Revoke the current session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### GET /auth/me

Get the current authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "title": "Quality Manager",
  "is_active": true,
  "is_superuser": false,
  "clearance_level": 2,
  "avatar_url": null,
  "last_login": "2025-01-15T10:00:00Z",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## Token Details

| Token | Lifetime | Contains |
|-------|----------|----------|
| Access token | 30 min (configurable) | `sub` (user ID), `exp`, `type: "access"`, `jti` (session ID) |
| Refresh token | 7 days (configurable) | `sub` (user ID), `exp`, `type: "refresh"` |

Tokens are signed with the `SECRET_KEY` using the `ALGORITHM` (default: HS256).

## Session Management

Sessions are tracked server-side via the `sessions` table. Each login creates a new session with a unique JTI (JWT Token ID) embedded in the access token.

Active sessions can be listed and revoked via the Users API (`GET /users/me/sessions`, `DELETE /users/me/sessions/{session_id}`).
