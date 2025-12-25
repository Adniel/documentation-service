# API Design Guide

Du hjälper användaren att designa API:er för Documentation Service.

## Argument
- `$ARGUMENTS` innehåller modulnamnet

## API-principer

### REST API Design

- **Resource-oriented** - Substantiv, inte verb
- **Plural resources** - `/documents`, inte `/document`
- **Nested resources** - `/spaces/{id}/documents`
- **HTTP-metoder** - GET, POST, PATCH, DELETE
- **Statuscodes** - Korrekta HTTP-statuskoder

### Vanliga mönster

```yaml
# List
GET /api/{resources}?page=1&limit=20&filter=value

# Get
GET /api/{resources}/{id}

# Create
POST /api/{resources}

# Update
PATCH /api/{resources}/{id}

# Delete
DELETE /api/{resources}/{id}

# Actions
POST /api/{resources}/{id}/{action}
```

---

## Modul-API:er

### content

```yaml
openapi: 3.0.0
info:
  title: Content API
  version: 1.0.0

paths:
  # Spaces
  /api/spaces:
    get:
      summary: List spaces in current workspace
      parameters:
        - name: workspace_id
          in: query
          schema: { type: string, format: uuid }
    post:
      summary: Create space
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSpace'

  /api/spaces/{id}:
    get:
      summary: Get space
    patch:
      summary: Update space
    delete:
      summary: Delete space

  # Documents
  /api/spaces/{space_id}/documents:
    get:
      summary: List documents in space
    post:
      summary: Create document

  /api/documents/{id}:
    get:
      summary: Get document with content
    patch:
      summary: Update document
    delete:
      summary: Move to trash

  /api/documents/{id}/content:
    get:
      summary: Get document content only
    put:
      summary: Update document content

  # Versions
  /api/documents/{id}/versions:
    get:
      summary: Get version history

  /api/documents/{id}/versions/{version}:
    get:
      summary: Get specific version

  /api/documents/{id}/restore:
    post:
      summary: Restore to specific version
      requestBody:
        content:
          application/json:
            schema:
              properties:
                version: { type: string }

components:
  schemas:
    CreateSpace:
      type: object
      required: [name, workspace_id]
      properties:
        name: { type: string }
        workspace_id: { type: string, format: uuid }
        description: { type: string }
```

### document-control

```yaml
paths:
  # Change Requests
  /api/documents/{id}/change-requests:
    get:
      summary: List change requests
    post:
      summary: Create change request (start draft)

  /api/change-requests/{id}:
    get:
      summary: Get change request details
    delete:
      summary: Cancel change request

  /api/change-requests/{id}/submit:
    post:
      summary: Submit for review

  /api/change-requests/{id}/approve:
    post:
      summary: Approve (with e-signature)
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ApprovalRequest'

  /api/change-requests/{id}/reject:
    post:
      summary: Reject with reason

  /api/change-requests/{id}/merge:
    post:
      summary: Merge approved changes

  # Workflows
  /api/workflows:
    get:
      summary: List workflow templates
    post:
      summary: Create workflow template

  /api/workflows/{id}/instances:
    get:
      summary: List active workflow instances

components:
  schemas:
    ApprovalRequest:
      type: object
      required: [password, meaning]
      properties:
        password: { type: string }
        mfa_code: { type: string }
        meaning:
          type: string
          enum: [Approved, Reviewed, Authored]
        comment: { type: string }
```

### signatures

```yaml
paths:
  /api/documents/{id}/signatures:
    get:
      summary: Get all signatures for document
    post:
      summary: Add signature
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SignatureRequest'

  /api/signatures/{id}/verify:
    get:
      summary: Verify signature integrity

components:
  schemas:
    SignatureRequest:
      type: object
      required: [password, meaning]
      properties:
        password: { type: string }
        mfa_code: { type: string }
        meaning:
          type: string
          enum: [Authored, Reviewed, Approved, Acknowledged]
        comment: { type: string }

    SignatureRecord:
      type: object
      properties:
        id: { type: string, format: uuid }
        user_id: { type: string, format: uuid }
        full_name: { type: string }
        title: { type: string }
        meaning: { type: string }
        timestamp: { type: string, format: date-time }
        git_sha: { type: string }
        content_hash: { type: string }
        verified: { type: boolean }
```

### access

```yaml
paths:
  # Permissions
  /api/spaces/{id}/permissions:
    get:
      summary: List permissions
    post:
      summary: Grant permission

  /api/permissions/{id}:
    delete:
      summary: Revoke permission

  # Classifications
  /api/documents/{id}/classification:
    get:
      summary: Get document classification
    put:
      summary: Set classification
      requestBody:
        content:
          application/json:
            schema:
              properties:
                level: { type: string, enum: [public, internal, confidential, restricted] }
                reason: { type: string }

  # Clearances
  /api/users/{id}/clearances:
    get:
      summary: Get user clearances
    post:
      summary: Grant clearance

  /api/clearances/{id}:
    delete:
      summary: Revoke clearance
```

### learning

```yaml
paths:
  # Assessments
  /api/documents/{id}/assessment:
    get:
      summary: Get assessment configuration
    put:
      summary: Configure assessment

  /api/assessments/{id}/questions:
    get:
      summary: Get questions (randomized for user)
    post:
      summary: Submit answers

  /api/assessments/{id}/generate:
    post:
      summary: Generate AI questions
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QuestionGenConfig'

  # Assignments
  /api/assignments:
    get:
      summary: List user's assignments
    post:
      summary: Create assignment

  /api/assignments/{id}:
    get:
      summary: Get assignment details

  /api/assignments/{id}/complete:
    post:
      summary: Complete assignment (with signature)

  # Learning Tracks
  /api/learning-tracks:
    get:
      summary: List learning tracks
    post:
      summary: Create learning track

components:
  schemas:
    QuestionGenConfig:
      type: object
      properties:
        sources:
          type: array
          items:
            type: object
            properties:
              type: { type: string, enum: [document, url, mcp] }
              id: { type: string }
        question_count: { type: integer }
        difficulty: { type: string, enum: [basic, standard, advanced] }
        question_types: { type: array, items: { type: string } }
```

### mcp

```yaml
# MCP Server endpoints (for external AI consumers)
paths:
  /mcp/tools/search_documents:
    post:
      summary: Search documents
      requestBody:
        content:
          application/json:
            schema:
              properties:
                query: { type: string }
                filters:
                  type: object
                  properties:
                    space: { type: string }
                    type: { type: string }
                    classification_max: { type: string }
                limit: { type: integer, default: 10 }

  /mcp/tools/get_document:
    post:
      summary: Get document content
      requestBody:
        content:
          application/json:
            schema:
              properties:
                id: { type: string }
                version: { type: string }

  /mcp/tools/get_document_section:
    post:
      summary: Get document section
      requestBody:
        content:
          application/json:
            schema:
              properties:
                id: { type: string }
                section_path: { type: string }

  # Service Accounts (admin)
  /api/mcp/service-accounts:
    get:
      summary: List service accounts
    post:
      summary: Create service account

  /api/mcp/service-accounts/{id}:
    get:
      summary: Get service account
    patch:
      summary: Update service account
    delete:
      summary: Delete service account
```

### audit

```yaml
paths:
  /api/audit:
    get:
      summary: Search audit events
      parameters:
        - name: resource_type
          in: query
        - name: resource_id
          in: query
        - name: actor_id
          in: query
        - name: event_type
          in: query
        - name: from
          in: query
          schema: { type: string, format: date-time }
        - name: to
          in: query
          schema: { type: string, format: date-time }

  /api/audit/export:
    post:
      summary: Export audit log
      requestBody:
        content:
          application/json:
            schema:
              properties:
                format: { type: string, enum: [csv, json] }
                filters: { type: object }

  /api/audit/reports/document-history/{id}:
    get:
      summary: Document history report

  /api/audit/reports/user-activity/{id}:
    get:
      summary: User activity report
```

---

## Error Responses

```yaml
components:
  schemas:
    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code: { type: string }
            message: { type: string }
            details: { type: object }

# Standard error codes
# 400 - Bad Request (validation errors)
# 401 - Unauthorized (not authenticated)
# 403 - Forbidden (not authorized)
# 404 - Not Found
# 409 - Conflict (version mismatch)
# 422 - Unprocessable Entity
# 500 - Internal Server Error
```

---

## Output

Generera:
1. **OpenAPI specification** (YAML/JSON)
2. **Route handlers** (baserat på valt backend)
3. **Request/Response types** (TypeScript eller motsvarande)
4. **Validation schemas** (Zod, Joi, Pydantic)
