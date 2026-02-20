# Content API Reference

Covers organizations, workspaces, spaces, pages, search, and navigation.

## Organizations

Base path: `/api/v1/organizations`

### POST /organizations

Create a new organization. The authenticated user becomes the owner.

**Request:**
```json
{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "description": "Acme Corporation documentation"
}
```

**Response (201):** `OrganizationResponse`

### GET /organizations

List organizations the current user belongs to.

**Response (200):** `OrganizationResponse[]`

### GET /organizations/{org_id}

Get a single organization by ID.

### PATCH /organizations/{org_id}

Update organization details. Requires Admin role.

**Request:**
```json
{
  "name": "Acme Corporation",
  "description": "Updated description"
}
```

## Workspaces

Base path: `/api/v1/workspaces`

### POST /workspaces

Create a workspace in an organization.

**Request:**
```json
{
  "name": "Quality Management",
  "slug": "quality-management",
  "description": "Quality system documentation",
  "organization_id": "org-uuid",
  "is_public": false
}
```

### GET /workspaces?organization_id={org_id}

List workspaces in an organization.

### GET /workspaces/{workspace_id}

Get a single workspace.

### PATCH /workspaces/{workspace_id}

Update workspace details. Requires Admin role.

## Spaces

Base path: `/api/v1/spaces`

### POST /spaces

Create a space in a workspace.

**Request:**
```json
{
  "name": "Tutorials",
  "slug": "tutorials",
  "description": "Learning-oriented documentation",
  "workspace_id": "workspace-uuid",
  "diataxis_type": "tutorial",
  "classification": "public"
}
```

**Diataxis types:** `tutorial`, `how_to`, `reference`, `explanation`, `mixed`

**Classification levels:** `public`, `internal`, `confidential`, `restricted`

### GET /spaces?workspace_id={workspace_id}

List spaces in a workspace, ordered by `sort_order`.

### GET /spaces/{space_id}

Get a single space.

### PATCH /spaces/{space_id}

Update space details. Supports changing `diataxis_type`, `classification`, `sort_order`.

## Pages

Base path: `/api/v1/content`

### POST /content/pages

Create a new page.

**Request:**
```json
{
  "title": "Getting Started with QMS",
  "slug": "getting-started-with-qms",
  "space_id": "space-uuid",
  "content": { "type": "doc", "content": [...] },
  "summary": "Introduction to the quality management system",
  "classification": "public",
  "diataxis_types": ["tutorial"]
}
```

- `content` — TipTap JSON document (optional, can be added later)
- `diataxis_types` — If `null`, inherits from the parent space
- `classification` — Defaults to `public`

**Response (201):** `PageResponse`

### GET /content/pages?space_id={space_id}

List pages in a space. Supports filtering:
- `space_id` (required)
- `diataxis_type` — Filter by type (optional)

### GET /content/pages/{page_id}

Get a single page with full content.

### PATCH /content/pages/{page_id}

Update page content and metadata.

**Request:**
```json
{
  "title": "Updated Title",
  "content": { "type": "doc", "content": [...] },
  "summary": "Updated summary",
  "classification": "internal",
  "diataxis_types": ["tutorial", "how_to"]
}
```

### DELETE /content/pages/{page_id}

Soft-delete a page (sets `is_active = false`).

### Change Requests

Change request endpoints share the `/api/v1/content` prefix:

#### POST /content/{page_id}/change-requests

Create a change request (draft) for an existing page.

**Request:**
```json
{
  "title": "Annual review update",
  "description": "Updated per Q4 review findings"
}
```

#### GET /content/{page_id}/change-requests

List change requests for a page.

#### PATCH /content/change-requests/{cr_id}

Update change request status (submit, approve, reject).

## Search

Base path: `/api/v1/search`

### GET /search?q={query}

Full-text search across accessible pages.

**Query parameters:**
- `q` — Search query (required)
- `organization_id` — Filter by organization
- `workspace_id` — Filter by workspace
- `space_id` — Filter by space
- `diataxis_type` — Filter by Diataxis type
- `status` — Filter by page status
- `limit` — Max results (default: 20)
- `offset` — Pagination offset

**Response (200):**
```json
{
  "hits": [
    {
      "id": "page-uuid",
      "title": "Getting Started",
      "slug": "getting-started",
      "summary": "...",
      "highlight": "...matched text...",
      "space_name": "Tutorials",
      "workspace_name": "Quality Management"
    }
  ],
  "total": 42,
  "query": "getting started"
}
```

Results are filtered by the user's clearance level — classified pages above the user's clearance are excluded.

## Navigation

Base path: `/api/v1/nav`

### GET /nav/tree?organization_id={org_id}

Get the full content tree for sidebar navigation.

**Response (200):**
```json
{
  "workspaces": [
    {
      "id": "ws-uuid",
      "name": "Quality Management",
      "slug": "quality-management",
      "spaces": [
        {
          "id": "space-uuid",
          "name": "Tutorials",
          "slug": "tutorials",
          "diataxis_type": "tutorial",
          "pages": [
            { "id": "page-uuid", "title": "Getting Started", "slug": "getting-started", "status": "effective" }
          ]
        }
      ]
    }
  ]
}
```

## Response Schema: PageResponse

```json
{
  "id": "uuid",
  "title": "Page Title",
  "slug": "page-title",
  "space_id": "space-uuid",
  "author_id": "user-uuid",
  "parent_id": null,
  "document_number": "SOP-QMS-001",
  "version": "1.0",
  "status": "effective",
  "classification": "public",
  "diataxis_types": ["tutorial"],
  "content": { "type": "doc", "content": [...] },
  "summary": "Brief description",
  "git_path": "quality-management/tutorials/page-title.json",
  "git_commit_sha": "abc123...",
  "is_active": true,
  "is_template": false,
  "sort_order": 0,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```
