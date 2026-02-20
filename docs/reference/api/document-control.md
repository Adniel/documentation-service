# Document Control API Reference

Base path: `/api/v1/document-control`

## Lifecycle Management

### GET /document-control/lifecycle/{page_id}

Get the current lifecycle state of a page.

**Response (200):**
```json
{
  "page_id": "uuid",
  "status": "effective",
  "version": "1.0",
  "revision": "A",
  "document_number": "SOP-QMS-001",
  "effective_date": "2025-01-15T00:00:00Z",
  "review_due_date": "2026-01-15T00:00:00Z",
  "transitions": ["obsolete", "archived"]
}
```

The `transitions` field lists valid next statuses from the current state.

### POST /document-control/lifecycle/{page_id}/transition

Transition a page to a new lifecycle status.

**Request:**
```json
{
  "target_status": "effective",
  "reason": "All approvals obtained, ready for release"
}
```

**Valid transitions:**

| From | To | Required |
|------|----|----------|
| `draft` | `in_review` | Author or Editor role |
| `in_review` | `draft` | Author (request changes) |
| `in_review` | `approved` | All approval matrix signatures |
| `approved` | `effective` | Admin or Owner role |
| `effective` | `obsolete` | Admin or Owner role |
| `effective` | `archived` | Admin or Owner role |
| `obsolete` | `archived` | Admin or Owner role |

## Document Numbering

### GET /document-control/numbering/config

Get the numbering configuration for an organization.

**Response (200):**
```json
{
  "enabled": true,
  "prefixes": {
    "sop": "SOP",
    "work_instruction": "WI",
    "policy": "POL",
    "form": "FRM",
    "reference": "REF",
    "specification": "SPEC"
  },
  "next_sequences": {
    "SOP-QUA": 4,
    "WI-ENG": 12
  }
}
```

### PUT /document-control/numbering/config

Update numbering configuration. Requires Admin role.

**Request:**
```json
{
  "prefixes": {
    "sop": "SOP",
    "work_instruction": "WI",
    "policy": "POL"
  }
}
```

## Approval Matrices

### GET /document-control/approval-matrices

List approval matrices for the organization.

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "SOP Approval",
    "document_types": ["sop"],
    "required_signatures": [
      { "role": "author", "meaning": "authored", "required": true },
      { "role": "reviewer", "meaning": "reviewed", "required": true },
      { "role": "admin", "meaning": "approved", "required": true }
    ]
  }
]
```

### POST /document-control/approval-matrices

Create an approval matrix. Requires Admin role.

**Request:**
```json
{
  "name": "Work Instruction Approval",
  "document_types": ["work_instruction"],
  "required_signatures": [
    { "role": "author", "meaning": "authored", "required": true },
    { "role": "editor", "meaning": "approved", "required": true }
  ]
}
```

### GET /document-control/approval-matrices/{matrix_id}

Get a single approval matrix.

### PUT /document-control/approval-matrices/{matrix_id}

Update an approval matrix.

### DELETE /document-control/approval-matrices/{matrix_id}

Delete an approval matrix.

## Retention Policies

### GET /document-control/retention-policies

List retention policies.

### POST /document-control/retention-policies

Create a retention policy.

**Request:**
```json
{
  "name": "Standard SOP Retention",
  "retention_days": 2555,
  "disposition_method": "archive",
  "expiration_action": "notify"
}
```

**Disposition methods:** `archive`, `destroy`, `review`

**Expiration actions:** `notify`, `auto_archive`, `manual_review`

### GET /document-control/retention-policies/{policy_id}

Get a single retention policy.

### PUT /document-control/retention-policies/{policy_id}

Update a retention policy.

### DELETE /document-control/retention-policies/{policy_id}

Delete a retention policy. Fails if documents are still assigned.

### GET /document-control/retention-policies/expiring

List documents nearing or past their retention expiration.

**Query parameters:**
- `days` — Lookahead window in days (default: 30)

**Response (200):**
```json
{
  "expiring_soon": [
    {
      "page_id": "uuid",
      "title": "Obsolete SOP",
      "document_number": "SOP-QMS-001",
      "retention_expires_at": "2025-03-01T00:00:00Z",
      "disposition_method": "archive"
    }
  ]
}
```
