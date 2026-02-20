# Audit Trail API Reference

The audit endpoints are registered without a prefix in the router but are accessible under the API prefix.

## Overview

The audit trail is an append-only, hash-chained event log. Every state-changing action is recorded. Events cannot be modified or deleted.

## Endpoints

### GET /api/v1/audit/events

List audit events with filtering and pagination.

**Query parameters:**
- `organization_id` — Filter by organization
- `user_id` — Filter by actor
- `event_type` — Filter by event type (e.g., `page.created`, `signature.applied`)
- `resource_type` — Filter by resource type (e.g., `page`, `user`, `organization`)
- `resource_id` — Filter by specific resource
- `from` — Start date (ISO 8601)
- `to` — End date (ISO 8601)
- `limit` — Max results (default: 50, max: 200)
- `offset` — Pagination offset

**Response (200):**
```json
{
  "events": [
    {
      "id": "event-uuid",
      "event_type": "page.status_changed",
      "resource_type": "page",
      "resource_id": "page-uuid",
      "user_id": "user-uuid",
      "user_email": "admin@example.com",
      "organization_id": "org-uuid",
      "details": {
        "from_status": "in_review",
        "to_status": "approved",
        "reason": "All signatures collected"
      },
      "event_hash": "sha256:abc123...",
      "previous_hash": "sha256:xyz789...",
      "timestamp": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 1234,
  "limit": 50,
  "offset": 0
}
```

### GET /api/v1/audit/events/{event_id}

Get a single audit event.

### GET /api/v1/audit/export

Export audit events for compliance reporting.

**Query parameters:**
- `from` — Start date (required)
- `to` — End date (required)
- `format` — Export format: `csv` or `json` (default: `json`)
- `organization_id` — Filter by organization

**Response:** File download with appropriate content type.

### GET /api/v1/audit/verify

Verify the integrity of the audit hash chain.

**Query parameters:**
- `organization_id` — Organization to verify
- `from` — Start of verification window
- `to` — End of verification window

**Response (200):**
```json
{
  "valid": true,
  "events_checked": 5432,
  "first_event": "2025-01-01T00:00:00Z",
  "last_event": "2025-01-15T10:00:00Z",
  "broken_links": []
}
```

If the chain is broken:
```json
{
  "valid": false,
  "events_checked": 5432,
  "broken_links": [
    {
      "event_id": "event-uuid",
      "expected_previous_hash": "sha256:abc...",
      "actual_previous_hash": "sha256:xyz...",
      "timestamp": "2025-01-10T14:30:00Z"
    }
  ]
}
```

## Event Types

### Content Events

| Event Type | Description |
|-----------|------------|
| `page.created` | New page created |
| `page.updated` | Page content or metadata updated |
| `page.deleted` | Page soft-deleted |
| `page.restored` | Page restored from deletion |
| `page.status_changed` | Lifecycle status transition |

### Signature Events

| Event Type | Description |
|-----------|------------|
| `signature.challenge_created` | Signature challenge initiated |
| `signature.applied` | Electronic signature completed |
| `signature.verified` | Signature verification performed |

### Access Events

| Event Type | Description |
|-----------|------------|
| `auth.login` | User logged in |
| `auth.logout` | User logged out |
| `auth.login_failed` | Failed login attempt |
| `permission.changed` | Permission or role updated |
| `classification.changed` | Content classification changed |

### Admin Events

| Event Type | Description |
|-----------|------------|
| `user.created` | New user account created |
| `user.updated` | User profile or settings changed |
| `organization.created` | New organization created |
| `member.added` | Member added to organization |
| `member.removed` | Member removed from organization |
| `config.changed` | System configuration updated |

### System Events

| Event Type | Description |
|-----------|------------|
| `system.seed` | Database seed operation |
| `import.completed` | Content import finished |
| `export.completed` | Content export generated |

## Hash Chain Structure

Each event's hash is computed as:

```
event_hash = SHA-256(event_id + event_type + timestamp + user_id + details_json + previous_hash)
```

The first event in the chain has `previous_hash = "genesis"`.

This ensures:
- **Insertion** of an event after the fact breaks subsequent hashes
- **Modification** of an event changes its hash, breaking the chain
- **Deletion** of an event creates a gap detectable by chain verification
