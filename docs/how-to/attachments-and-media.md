# How to Manage Attachments and Media

This guide covers uploading files, managing attachments, and embedding images in your documents.

## Overview

The Attachments module supports file uploads with two storage backends: local filesystem and S3-compatible object storage. Files are associated with pages and can be embedded inline in the editor.

## Upload a File

### Via the Editor

1. Open a page in the editor
2. Use one of these methods:
   - Type `/image` to insert an image block, then select a file
   - Drag and drop a file into the editor
   - Click the **Attach** button in the toolbar
3. The file uploads and appears inline (images) or as an attachment link (other files)

### Via the API

```
POST /api/v1/attachments/upload
Content-Type: multipart/form-data

file: (binary)
page_id: "page-uuid"
description: "Architecture diagram v2"
```

Response:

```json
{
  "id": "attachment-uuid",
  "filename": "architecture-v2.png",
  "content_type": "image/png",
  "size_bytes": 245632,
  "url": "/api/v1/attachments/attachment-uuid/download",
  "status": "active"
}
```

## File Size Limits

The maximum file size is configured via `ATTACHMENT_MAX_FILE_SIZE_MB` (default: 100 MB).

## Supported File Types

All file types are accepted. Common types include:

| Category | Extensions |
|----------|-----------|
| Images | .png, .jpg, .jpeg, .gif, .svg, .webp |
| Documents | .pdf, .docx, .xlsx, .pptx |
| Archives | .zip, .tar.gz |
| Code | .py, .js, .ts, .json, .yaml |
| Data | .csv, .xml |

## List Attachments

View all attachments for a page:

```
GET /api/v1/attachments?page_id={page_id}
```

Or list all attachments in an organization:

```
GET /api/v1/attachments?organization_id={org_id}
```

## Download an Attachment

```
GET /api/v1/attachments/{attachment_id}/download
```

This returns the file with appropriate `Content-Type` and `Content-Disposition` headers.

## Delete an Attachment

```
DELETE /api/v1/attachments/{attachment_id}
```

This soft-deletes the attachment (sets status to "deleted"). The file remains in storage for retention compliance but is no longer accessible via the API.

## Inline Images in the Editor

When you upload an image through the editor, it creates an inline image block:

1. The image is uploaded to the attachments API
2. A TipTap image node is inserted with the attachment URL as the `src`
3. The image renders inline in the editor and published output

To resize an inline image, click it and drag the resize handles.

## Storage Backend Configuration

### Local Storage (Default)

Files are stored on the filesystem at the path configured by `ATTACHMENT_STORAGE_PATH` (default: `/tmp/docservice/attachments`).

For production, set this to a persistent, backed-up directory:

```env
ATTACHMENT_STORAGE_BACKEND=local
ATTACHMENT_STORAGE_PATH=/var/lib/docservice/attachments
```

### S3-Compatible Storage

For scalable, cloud-based storage:

```env
ATTACHMENT_STORAGE_BACKEND=s3
ATTACHMENT_S3_BUCKET=my-docs-attachments
ATTACHMENT_S3_REGION=us-east-1
ATTACHMENT_S3_ACCESS_KEY=AKIA...
ATTACHMENT_S3_SECRET_KEY=...
```

For MinIO or other S3-compatible services, also set:

```env
ATTACHMENT_S3_ENDPOINT_URL=http://minio:9000
```

See [Configuration Reference](../reference/configuration.md) for all attachment settings.
