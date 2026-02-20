# Approval Workflow

This tutorial walks you through the full document lifecycle: drafting, submitting for review, getting approval, and making a document effective.

## Prerequisites

- Completed [Create Your First Document](create-first-document.md)
- A page in Draft status
- At least two users: one author and one reviewer/approver

## Document Lifecycle Overview

Every page follows a controlled lifecycle:

```
Draft → In Review → Approved → Effective → Obsolete
                                    ↓
                                 Archived
```

| Status | Meaning |
|--------|---------|
| **Draft** | Being written or edited. Only the author and editors can see it. |
| **In Review** | Submitted for review. Reviewers can comment and request changes. |
| **Approved** | All required approvals obtained. Ready to be made effective. |
| **Effective** | The current live version. Read-only until a new change request is created. |
| **Obsolete** | Superseded by a newer version or no longer applicable. |
| **Archived** | Retained for records but removed from active navigation. |

## Step 1: Create a Change Request

When your page is in Draft or you want to edit an Effective page:

1. Click **Edit** on the page (or **Create Change Request** for effective pages)
2. A change request (CR) is created automatically
3. Behind the scenes, a Git branch is created: `draft/CR-{id}`
4. Edit the content — all saves go to the draft branch

**API equivalent:**

```
POST /api/v1/content/{page_id}/change-requests
{
  "title": "Update safety procedures",
  "description": "Revised per annual review findings"
}
```

## Step 2: Submit for Review

When your changes are ready:

1. Click **Submit for Review** in the page toolbar
2. Optionally add a submission note
3. The page status changes to **In Review**

Reviewers assigned via the approval matrix are notified.

## Step 3: Review Process

Reviewers can:

- **Comment** — Add inline or page-level comments
- **Approve** — Sign off on the changes
- **Request Changes** — Send back to the author with feedback

### Viewing the Diff

Click **View Changes** to see a side-by-side diff comparing the draft against the current effective version. This uses the Git diff between the draft branch and main.

## Step 4: Approval and Electronic Signatures

When a reviewer approves, they provide an electronic signature (21 CFR Part 11 compliant):

1. Reviewer clicks **Approve**
2. A signature challenge is created — the reviewer must re-authenticate
3. The reviewer enters their password and selects a signature meaning:
   - **Authored** — I wrote this content
   - **Reviewed** — I reviewed this content for accuracy
   - **Approved** — I approve this content for release
   - **Witnessed** — I witnessed this approval
4. The signature captures:
   - Content hash (SHA-256) for integrity
   - NTP-sourced timestamp
   - Signer identity and meaning

**API flow:**

```
POST /api/v1/signatures/challenge
{ "page_id": "...", "meaning": "approved" }

→ Returns { "challenge_id": "..." }

POST /api/v1/signatures/sign
{
  "challenge_id": "...",
  "password": "reviewer-password",
  "meaning": "approved",
  "comment": "Reviewed and approved per SOP-QMS-001"
}
```

### Approval Matrix

The required approvals are defined by the **Approval Matrix** configured for the document type:

- SOPs may require: Author + Reviewer + Quality Approver
- Work Instructions may require: Author + Department Lead
- Policies may require: Author + Management Representative

## Step 5: Make Effective

Once all required approvals are collected:

1. An authorized user clicks **Make Effective**
2. The draft branch is merged into main (Git merge with `--no-ff`)
3. The page status changes to **Effective**
4. The previous effective version (if any) is marked **Obsolete**
5. An audit event is recorded

The effective date is captured, and the document is now the live version.

## Step 6: View Audit Trail

Every action in the workflow is recorded in the immutable audit trail:

1. Navigate to the page
2. Click **Audit Log** in the toolbar
3. View all events: creation, edits, submissions, approvals, status changes

Each audit event includes a cryptographic hash linking it to the previous event, forming a tamper-evident chain.

## Next Steps

- [Document Numbering](../how-to/document-numbering.md) — Assign controlled document numbers
- [Training and Assessments](training-and-assessments.md) — Require acknowledgment of effective documents
