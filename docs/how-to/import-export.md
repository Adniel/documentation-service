# How to Import and Export Content

This guide covers exporting documentation as ZIP bundles and importing content from Markdown files or Confluence.

## Export

### Export a Single Page

```
GET /api/v1/portability/export/page/{page_id}?format=markdown
```

Supported formats:
- `markdown` — Standard Markdown with front matter
- `json` — TipTap JSON document format
- `html` — Rendered HTML

### Export a Space

Export all pages in a space as a ZIP bundle:

```
GET /api/v1/portability/export/space/{space_id}?format=markdown
```

The ZIP contains:
```
space-slug/
├── _meta.json          # Space metadata
├── page-one.md
├── page-two.md
└── attachments/
    ├── diagram.png
    └── spec.pdf
```

### Export a Workspace

Export an entire workspace:

```
GET /api/v1/portability/export/workspace/{workspace_id}?format=markdown
```

ZIP structure:
```
workspace-slug/
├── _meta.json
├── tutorials/
│   ├── _meta.json
│   ├── getting-started.md
│   └── first-document.md
├── how-to-guides/
│   ├── _meta.json
│   └── configure-approvals.md
└── reference/
    ├── _meta.json
    └── api-endpoints.md
```

### Metadata Front Matter

Exported Markdown files include YAML front matter:

```markdown
---
title: "Getting Started"
slug: "getting-started"
document_number: "SOP-QMS-001"
version: "1.0"
status: "effective"
classification: "public"
diataxis_types: ["tutorial"]
author: "admin@acme-corp.example"
created_at: "2025-01-15T10:00:00Z"
updated_at: "2025-02-01T14:30:00Z"
---

# Getting Started

Content here...
```

## Import

### Import Markdown Files

Upload a ZIP of Markdown files to create pages:

```
POST /api/v1/portability/import
Content-Type: multipart/form-data

file: (ZIP binary)
target_space_id: "space-uuid"
format: "markdown"
conflict_resolution: "skip"
```

Options for `conflict_resolution`:
- `skip` — Skip pages with matching slugs (default)
- `overwrite` — Replace existing pages with imported content
- `rename` — Append a suffix to avoid conflicts

### Import from Confluence

Export your Confluence space as HTML, then import:

```
POST /api/v1/portability/import
Content-Type: multipart/form-data

file: (Confluence HTML export ZIP)
target_space_id: "space-uuid"
format: "confluence"
conflict_resolution: "skip"
```

The importer:
1. Parses Confluence HTML export structure
2. Converts HTML content to TipTap JSON blocks
3. Preserves page hierarchy (parent-child relationships)
4. Extracts and re-uploads inline images as attachments
5. Maps Confluence macros to equivalent blocks where possible

### Import Format Detection

If the `format` parameter is omitted, the platform auto-detects based on file contents:

| Indicator | Detected Format |
|-----------|----------------|
| `.md` files with YAML front matter | `markdown` (platform native) |
| `.md` files without front matter | `markdown` (generic) |
| `entities.xml` or `exportDescriptor.properties` | `confluence` |
| `.json` files with TipTap structure | `json` (platform native) |

### Import Report

After import, the API returns a summary:

```json
{
  "total_files": 25,
  "imported": 22,
  "skipped": 2,
  "errors": 1,
  "details": [
    { "file": "overview.md", "status": "imported", "page_id": "..." },
    { "file": "existing.md", "status": "skipped", "reason": "slug exists" },
    { "file": "broken.md", "status": "error", "reason": "invalid content" }
  ]
}
```

## Best Practices

1. **Export before major changes** — Create a backup export before bulk operations
2. **Use platform format for round-trips** — Export as JSON for lossless re-import
3. **Verify after import** — Review imported pages for formatting issues
4. **Attachments are included** — ZIP exports contain referenced attachment files
5. **Classification is preserved** — Imported pages retain their classification level
