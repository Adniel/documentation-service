# Security Model

This document explains the dual-dimension access control model used by the platform, covering role-based permissions, classification-based clearance, and how they work together.

## Dual-Dimension Access Control

Access to content requires passing two independent checks:

```
                    ┌─────────────────┐
                    │  Access Request  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼─────────┐       ┌──────────▼──────────┐
    │  Role Check        │       │  Classification     │
    │  (Hierarchical)    │       │  Check (Clearance)  │
    └─────────┬─────────┘       └──────────┬──────────┘
              │                             │
              │     Both must grant         │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │  Access Granted  │
                    │  or Denied       │
                    └─────────────────┘
```

### Dimension 1: Role-Based (Hierarchical)

Roles determine what actions a user can perform. They are assigned per-organization and inherited through the content hierarchy:

| Role | Capabilities |
|------|-------------|
| **Owner** | Full control. Manage members, delete organization, all admin actions. |
| **Admin** | Manage workspaces, spaces, permissions. Cannot delete the organization. |
| **Editor** | Create and edit pages. Submit change requests. Cannot manage permissions. |
| **Reviewer** | Review and approve documents. Cannot create new content. |
| **Viewer** | Read-only access to content within their clearance level. |

Roles follow a strict hierarchy: each role includes all capabilities of the roles below it.

### Dimension 2: Classification-Based (Clearance)

Classification controls visibility based on content sensitivity and user clearance:

| Level | Value | Description |
|-------|-------|-------------|
| **Public** | 0 | Visible to all authenticated users |
| **Internal** | 1 | Visible to users with clearance ≥ 1 |
| **Confidential** | 2 | Visible to users with clearance ≥ 2 |
| **Restricted** | 3 | Visible to users with clearance ≥ 3 |

A user can only see content at or below their clearance level. Classification is set at the space level and can be overridden per page.

### Why Two Dimensions?

Consider this scenario:

- **Alice** is an Editor (role) with clearance level 1 (Internal)
- A page is marked Confidential (classification 2)
- Alice has the **role** to edit pages, but not the **clearance** to see this one
- Result: Alice cannot access the page

This prevents role escalation from granting access to sensitive content. An admin who manages permissions (high role) but has low clearance cannot read classified documents.

## Authentication

### JWT Tokens

The platform uses stateless JWT tokens for API authentication:

- **Access tokens** — Short-lived (default: 30 minutes), used for API requests
- **Refresh tokens** — Longer-lived (default: 7 days), used to obtain new access tokens
- **JTI (JWT Token ID)** — Optional session tracking, enables server-side revocation

Token payload:
```json
{
  "sub": "user-uuid",
  "exp": 1700000000,
  "type": "access",
  "jti": "session-uuid"
}
```

### Session Management

Sessions are tracked server-side for security:

- Each login creates a `Session` record in the database
- Sessions can be revoked individually or all-at-once (force logout)
- Inactive sessions expire automatically (configurable timeout)
- Failed login attempts are tracked; accounts lock after repeated failures

### Password Security

Passwords are hashed with **Argon2** (via passlib):

- Memory-hard algorithm resistant to GPU/ASIC attacks
- No 72-byte length limit (unlike bcrypt)
- Automatic salt generation
- Configurable memory cost, time cost, and parallelism

## Permission Evaluation

When a user requests access to a resource, the following checks run in order:

1. **Authentication** — Is the JWT valid and not expired?
2. **Session validity** — Is the session active and not revoked?
3. **Account status** — Is the user active and not locked?
4. **Organization membership** — Is the user a member of the resource's organization?
5. **Role check** — Does the user's role grant the required capability?
6. **Classification check** — Is the user's clearance ≥ the content's classification?

If any check fails, access is denied with an appropriate HTTP status code (401 or 403).

## Document-Level Overrides

While permissions are primarily inherited from the content hierarchy, individual pages can have explicit ACL overrides:

- **Grant** — Give a specific user access they wouldn't otherwise have
- **Deny** — Remove access from a specific user despite their role

Overrides are evaluated after the standard role and classification checks and can either widen or narrow access for individual users.

## Service Accounts

For MCP integration and API automation, the platform supports service accounts:

- Created per-organization by admins
- Have a fixed role and clearance level
- Authenticate via API keys (not passwords)
- All actions are audited with the service account identity
- Rate-limited to prevent abuse

See [MCP Integration](../how-to/mcp-integration.md) for setup instructions.

## Published Site Access

Published documentation sites have a separate visitor access model:

- **Public** sites are accessible without authentication
- **Restricted** sites require visitor authentication (email-based)
- **Visitor roles** are separate from organization roles
- Classification-restricted pages show placeholders or are hidden entirely

See [Publishing Sites](../how-to/publishing-sites.md) for configuration.
