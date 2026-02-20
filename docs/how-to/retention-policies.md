# How to Configure Retention Policies

This guide shows you how to set up document retention periods and disposition methods.

## Overview

Retention policies define how long documents are kept after they become obsolete and what happens when the retention period expires. This supports ISO 15489 records management requirements.

## Create a Retention Policy

1. Navigate to **Admin** → **Document Control** → **Retention Policies**
2. Click **New Policy**
3. Fill in the fields:
   - **Name**: e.g., "Standard SOP Retention"
   - **Document types**: Which document types this applies to
   - **Retention period**: Duration in days, months, or years
   - **Disposition method**: What happens after the period ends
   - **Expiration action**: What to do when the period is about to expire
4. Click **Create**

**API:**

```
POST /api/v1/document-control/retention-policies
{
  "name": "Standard SOP Retention",
  "retention_days": 2555,
  "disposition_method": "archive",
  "expiration_action": "notify"
}
```

## Disposition Methods

| Method | Description |
|--------|------------|
| **Archive** | Move to read-only archive. Content preserved but removed from active navigation. |
| **Destroy** | Permanently delete the document and all versions. Irreversible. |
| **Review** | Flag for manual review. An admin must decide whether to archive or extend. |

## Expiration Actions

| Action | Description |
|--------|------------|
| **Notify** | Send email/notification to the document owner and org admins. |
| **Auto-archive** | Automatically archive when the retention period expires. |
| **Manual review** | Create a review task assigned to the document owner. |

## Typical Retention Periods

| Document Type | Suggested Retention | Rationale |
|--------------|-------------------|-----------|
| SOPs | 7 years after obsolescence | ISO 13485 §4.2.5 |
| Training records | Life of device + 2 years | 21 CFR 820.184 |
| Audit reports | 7 years | Standard quality practice |
| Design documents | Life of product | ISO 13485 §4.2.5 |
| Policies | 5 years after replacement | Organizational practice |

## Assign a Policy to Documents

Retention policies are applied at the space or page level:

### Space-Level (Bulk)

All pages in the space inherit the retention policy:

```
PATCH /api/v1/spaces/{space_id}
{
  "retention_policy_id": "policy-uuid"
}
```

### Page-Level (Override)

Override the space policy for a specific page:

```
PATCH /api/v1/content/pages/{page_id}
{
  "retention_policy_id": "policy-uuid"
}
```

## Monitor Retention Status

View upcoming expirations from the admin dashboard:

1. Navigate to **Admin** → **Document Control** → **Retention Dashboard**
2. Filter by:
   - **Expiring soon** — Within 30/60/90 days
   - **Expired** — Past retention date, pending disposition
   - **Archived** — Already archived by retention policy
3. Take action on individual documents or in bulk

**API:**

```
GET /api/v1/document-control/retention-policies/expiring?days=30
```
