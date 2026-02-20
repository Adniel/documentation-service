# Attachments API Reference

Base path: `/api/v1/attachments`

## Endpoints

### POST /attachments/upload

Upload a file attachment.

**Request:** `multipart/form-data`
- `file` — Binary file data (required)
- `page_id` — Associated page UUID (required)
- `description` — Optional description

**Response (201):**
```json
{
  "id": "attachment-uuid",
  "filename": "architecture-diagram.png",
  "original_filename": "architecture-diagram.png",
  "content_type": "image/png",
  "size_bytes": 245632,
  "page_id": "page-uuid",
  "uploaded_by": "user-uuid",
  "description": "System architecture overview",
  "status": "active",
  "url": "/api/v1/attachments/attachment-uuid/download",
  "created_at": "2025-01-15T10:00:00Z"
}
```

**Errors:**
- `400` — File exceeds `ATTACHMENT_MAX_FILE_SIZE_MB` limit
- `400` — No file provided
- `404` — Page not found
- `403` — Insufficient permissions

### GET /attachments

List attachments with filtering.

**Query parameters:**
- `page_id` — Filter by page
- `organization_id` — Filter by organization
- `status` — Filter by status: `active`, `deleted`
- `content_type` — Filter by MIME type prefix (e.g., `image/`)
- `limit` — Max results (default: 50)
- `offset` — Pagination offset

**Response (200):**
```json
{
  "attachments": [
    {
      "id": "attachment-uuid",
      "filename": "architecture-diagram.png",
      "content_type": "image/png",
      "size_bytes": 245632,
      "page_id": "page-uuid",
      "status": "active",
      "url": "/api/v1/attachments/attachment-uuid/download",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 15
}
```

### GET /attachments/{attachment_id}

Get attachment metadata.

### GET /attachments/{attachment_id}/download

Download the file. Returns the binary content with appropriate headers:

```
Content-Type: image/png
Content-Disposition: inline; filename="architecture-diagram.png"
Content-Length: 245632
```

For non-image files, `Content-Disposition` uses `attachment` instead of `inline`.

### PATCH /attachments/{attachment_id}

Update attachment metadata (description only).

**Request:**
```json
{
  "description": "Updated architecture diagram v2"
}
```

### DELETE /attachments/{attachment_id}

Soft-delete an attachment. Sets `status` to `deleted`. The file remains in storage for retention compliance but is excluded from listings and downloads.

**Response (200):**
```json
{
  "message": "Attachment deleted"
}
```

## Storage Backends

The storage backend is configured via `ATTACHMENT_STORAGE_BACKEND`:

### Local Storage

Files are stored at `ATTACHMENT_STORAGE_PATH` in a structured directory:

```
{ATTACHMENT_STORAGE_PATH}/
  {org-id}/
    {page-id}/
      {attachment-id}_{filename}
```

### S3 Storage

Files are stored in `ATTACHMENT_S3_BUCKET` with key pattern:

```
{org-id}/{page-id}/{attachment-id}_{filename}
```

See [Configuration Reference](../configuration.md) for all storage settings.

## Size Limits

| Setting | Default | Description |
|---------|---------|-------------|
| `ATTACHMENT_MAX_FILE_SIZE_MB` | 100 | Maximum single file size |

The upload endpoint validates file size before storage. Oversized files are rejected with a `400` error.
