# Permissions Reference

This document describes the role hierarchy, classification levels, and access control list (ACL) system.

## Role Hierarchy

Roles are assigned per-organization via the `organization_members` table. Each role inherits all capabilities of lower roles.

```
Owner
  └── Admin
        └── Editor
              └── Reviewer
                    └── Viewer
```

### Role Capabilities

| Capability | Owner | Admin | Editor | Reviewer | Viewer |
|-----------|-------|-------|--------|----------|--------|
| Delete organization | Yes | - | - | - | - |
| Manage members | Yes | Yes | - | - | - |
| Manage permissions | Yes | Yes | - | - | - |
| Configure approval matrices | Yes | Yes | - | - | - |
| Create/delete workspaces | Yes | Yes | - | - | - |
| Create/delete spaces | Yes | Yes | - | - | - |
| Create pages | Yes | Yes | Yes | - | - |
| Edit pages | Yes | Yes | Yes | - | - |
| Submit change requests | Yes | Yes | Yes | - | - |
| Review/approve documents | Yes | Yes | Yes | Yes | - |
| Sign documents | Yes | Yes | Yes | Yes | - |
| View content | Yes | Yes | Yes | Yes | Yes |
| Search | Yes | Yes | Yes | Yes | Yes |

## Classification Levels

Content classification restricts visibility based on user clearance level. A user can see content at or below their clearance.

| Level | Name | Value | Description |
|-------|------|-------|-------------|
| 0 | **Public** | `public` | No access restriction |
| 1 | **Internal** | `internal` | Internal company content |
| 2 | **Confidential** | `confidential` | Sensitive business information |
| 3 | **Restricted** | `restricted` | Highest sensitivity, need-to-know basis |

### Classification Inheritance

- Spaces have a classification level (default: Public)
- Pages inherit their space's classification by default
- Pages can override to a higher or lower classification
- Search results are filtered by the user's clearance level

### User Clearance

Users have a `clearance_level` field (integer 0–3):

| Clearance | Can Access |
|-----------|-----------|
| 0 | Public only |
| 1 | Public + Internal |
| 2 | Public + Internal + Confidential |
| 3 | All levels |

Clearance is set by organization admins and is separate from the user's role.

## Access Evaluation

Access requires passing both dimensions:

```python
def has_access(user, resource):
    # Dimension 1: Role check
    if user.role_level < required_role_level(action):
        return False

    # Dimension 2: Classification check
    if user.clearance_level < resource.classification:
        return False

    # Both passed
    return True
```

### Evaluation Order

1. Is the user authenticated? (401 if not)
2. Is the user's session valid? (401 if expired/revoked)
3. Is the user active and not locked? (403 if not)
4. Is the user a member of the organization? (403 if not)
5. Does the user's role allow the action? (403 if not)
6. Is the user's clearance sufficient? (403 if not)
7. Are there page-level ACL overrides? (apply if present)

## Page-Level ACLs

Individual pages can have explicit access control entries:

```
POST /api/v1/permissions/pages/{page_id}/acl
{
  "user_id": "user-uuid",
  "grant": true
}
```

| Override | Effect |
|----------|--------|
| `grant: true` | User can access this page regardless of classification |
| `grant: false` | User cannot access this page regardless of role/clearance |

ACL overrides are evaluated after standard role and classification checks.

## Service Account Permissions

Service accounts follow the same permission model but:

- Authenticate via API keys instead of passwords
- Cannot sign documents (no password for re-authentication)
- Have fixed role and clearance (set at creation, changed by admins)
- All actions are rate-limited

## Published Site Visitor Permissions

Visitors to published sites have a separate permission model:

| Visitor Role | Access |
|-------------|--------|
| **Public** | Can view public pages on public sites |
| **Registered** | Can view pages up to their assigned classification level |
| **Admin** | Can view all published pages |

Visitor roles are managed per-site, independent of organization membership.
