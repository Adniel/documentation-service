# Electronic Signatures API Reference

Electronic signatures are 21 CFR Part 11 compliant. All signing requires re-authentication.

The signature endpoints are registered without a prefix in the router but are accessible under the API prefix.

## Challenge-Based Signing Flow

```
1. POST /signatures/challenge    → Get a challenge (valid 5 min)
2. POST /signatures/sign         → Sign with password + challenge
3. GET  /signatures/{id}/verify  → Verify signature integrity
```

## Endpoints

### POST /api/v1/signatures/challenge

Create a signature challenge. The user must complete the challenge within the expiry window (default: 5 minutes).

**Request:**
```json
{
  "page_id": "page-uuid",
  "meaning": "approved"
}
```

**Signature meanings:** `authored`, `reviewed`, `approved`, `witnessed`

**Response (200):**
```json
{
  "challenge_id": "challenge-uuid",
  "expires_at": "2025-01-15T10:05:00Z",
  "page_id": "page-uuid",
  "meaning": "approved"
}
```

### POST /api/v1/signatures/sign

Complete a signature by providing the password and challenge ID.

**Request:**
```json
{
  "challenge_id": "challenge-uuid",
  "password": "user-password",
  "meaning": "approved",
  "comment": "Reviewed and approved per SOP-QMS-001 requirements"
}
```

**Response (201):**
```json
{
  "id": "signature-uuid",
  "signer_id": "user-uuid",
  "signer_name": "Jane Doe",
  "signer_email": "jane@example.com",
  "page_id": "page-uuid",
  "meaning": "approved",
  "comment": "Reviewed and approved per SOP-QMS-001 requirements",
  "content_hash": "sha256:abc123...",
  "timestamp": "2025-01-15T10:01:30Z",
  "timestamp_source": "ntp",
  "git_commit_sha": "def456..."
}
```

**Errors:**
- `400` — Challenge expired or already used
- `401` — Invalid password
- `404` — Challenge not found
- `409` — Signature already exists for this user/page/meaning combination

### GET /api/v1/signatures/{signature_id}

Get a signature record.

**Response (200):** Full signature details as above.

### GET /api/v1/signatures/{signature_id}/verify

Verify signature integrity by recomputing the content hash.

**Response (200):**
```json
{
  "valid": true,
  "signature_id": "signature-uuid",
  "signer_name": "Jane Doe",
  "meaning": "approved",
  "content_hash_match": true,
  "original_hash": "sha256:abc123...",
  "current_hash": "sha256:abc123...",
  "timestamp": "2025-01-15T10:01:30Z"
}
```

If the content has changed since signing:
```json
{
  "valid": false,
  "content_hash_match": false,
  "original_hash": "sha256:abc123...",
  "current_hash": "sha256:xyz789...",
  "reason": "Content has been modified since signature was applied"
}
```

### GET /api/v1/signatures?page_id={page_id}

List all signatures for a page.

**Response (200):**
```json
{
  "signatures": [
    {
      "id": "sig-uuid-1",
      "signer_name": "Author Name",
      "meaning": "authored",
      "timestamp": "2025-01-14T09:00:00Z"
    },
    {
      "id": "sig-uuid-2",
      "signer_name": "Reviewer Name",
      "meaning": "reviewed",
      "timestamp": "2025-01-14T14:00:00Z"
    },
    {
      "id": "sig-uuid-3",
      "signer_name": "Approver Name",
      "meaning": "approved",
      "timestamp": "2025-01-15T10:01:30Z"
    }
  ]
}
```

## Signature Record Fields

| Field | Description |
|-------|-------------|
| `id` | Unique signature identifier |
| `signer_id` | User UUID of the signer |
| `signer_name` | Full name at time of signing |
| `signer_email` | Email at time of signing |
| `page_id` | Page that was signed |
| `meaning` | Signature meaning (authored/reviewed/approved/witnessed) |
| `comment` | Optional signer comment |
| `content_hash` | SHA-256 hash of the page content at signing time |
| `timestamp` | NTP-sourced timestamp |
| `timestamp_source` | Source of timestamp (`ntp` or `system`) |
| `git_commit_sha` | Git commit SHA at signing time |
| `created_at` | Record creation timestamp |
