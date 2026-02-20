# How to Configure Document Numbering

This guide shows you how to set up and customize automatic document numbering (e.g., SOP-QMS-001).

## Overview

The platform generates unique document numbers following a configurable pattern:

```
{PREFIX}-{CATEGORY}-{SEQUENCE}
```

Examples: `SOP-QMS-001`, `WI-ENG-042`, `POL-HR-003`

## Enable Document Numbering

Document numbering is enabled per organization.

1. Navigate to **Organization Settings**
2. Toggle **Document Numbering** to On
3. Click **Save**

**API:**

```
PATCH /api/v1/organizations/{org_id}
{
  "doc_numbering_enabled": true
}
```

## Configure Prefixes

Each document type has a default prefix:

| Document Type | Default Prefix | Description |
|--------------|----------------|-------------|
| SOP | `SOP` | Standard Operating Procedure |
| WI | `WI` | Work Instruction |
| POL | `POL` | Policy |
| FRM | `FRM` | Form/Template |
| REF | `REF` | Reference Document |
| SPEC | `SPEC` | Specification |

To customize prefixes, use the Document Control API:

```
PUT /api/v1/document-control/numbering/config
{
  "prefixes": {
    "sop": "SOP",
    "work_instruction": "WI",
    "policy": "POL",
    "form": "FRM",
    "reference": "REF",
    "specification": "SPEC"
  }
}
```

## How Numbers Are Assigned

1. When a page transitions to "In Review" for the first time, a document number is assigned
2. The sequence number auto-increments per prefix-category combination
3. Numbers are never reused, even if a document is deleted
4. The category code is derived from the workspace slug (uppercase, truncated to 3 characters)

### Example Sequence

| Page | Workspace | Type | Assigned Number |
|------|-----------|------|----------------|
| First SOP | Quality Management | SOP | SOP-QUA-001 |
| Second SOP | Quality Management | SOP | SOP-QUA-002 |
| First WI | Engineering | WI | WI-ENG-001 |
| Third SOP | Quality Management | SOP | SOP-QUA-003 |

## Manual Number Assignment

For migrated documents that already have established numbers:

```
PATCH /api/v1/content/pages/{page_id}
{
  "document_number": "SOP-QMS-001-LEGACY"
}
```

Manual numbers bypass the auto-increment system but must still be unique within the organization.

## View Document Numbers

Document numbers appear in:

- Page header (below the title)
- Search results
- Navigation sidebar (if enabled)
- Exported documents (PDF headers, ZIP manifests)
- Audit trail events
