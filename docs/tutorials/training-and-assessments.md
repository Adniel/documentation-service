# Training and Assessments

This tutorial shows you how to set up training assessments for documents and track user acknowledgments.

## Prerequisites

- Admin or Editor role
- At least one effective document
- Understanding of the [Approval Workflow](approval-workflow.md)

## Overview

The Learning module lets you:

1. Create assessments linked to documents
2. Define questions (multiple choice, true/false, open-ended)
3. Assign assessments to users
4. Require acknowledgment of effective documents
5. Track completion and certification

## Step 1: Create an Assessment

1. Navigate to an effective page
2. Click **Learning** → **Create Assessment**
3. Fill in:
   - **Title**: e.g., "SOP-QMS-001 Comprehension Check"
   - **Passing Score**: Percentage required to pass (default: 80%)
   - **Max Attempts**: How many tries users get (default: 3)
4. Click **Create**

**API equivalent:**

```
POST /api/v1/learning/assessments
{
  "page_id": "...",
  "title": "SOP-QMS-001 Comprehension Check",
  "passing_score": 80,
  "max_attempts": 3
}
```

## Step 2: Add Questions

Add questions to your assessment:

1. Click **Add Question**
2. Select the question type:
   - **Multiple Choice** — One correct answer from options
   - **True/False** — Binary choice
   - **Open Ended** — Free-text response (manually graded)
3. Enter the question text and options
4. Mark the correct answer
5. Optionally add an explanation shown after the attempt

### Example Questions

**Multiple Choice:**
> What is the first step in the document approval process?
> - A) Make the document effective
> - B) Submit for review ✓
> - C) Archive the document
> - D) Create a retention policy

**True/False:**
> Electronic signatures require re-authentication at signature time.
> - True ✓
> - False

## Step 3: Assign to Users

Assign the assessment to specific users or groups:

1. Click **Assignments** → **New Assignment**
2. Select users individually or by role
3. Set a **due date** (optional)
4. Click **Assign**

Assigned users receive a notification and see the assessment in their learning dashboard.

**API equivalent:**

```
POST /api/v1/learning/assignments
{
  "assessment_id": "...",
  "user_ids": ["user-1-id", "user-2-id"],
  "due_date": "2025-03-01T00:00:00Z"
}
```

## Step 4: Users Complete the Assessment

From the learner's perspective:

1. Open the learning dashboard or follow the notification link
2. Click **Start Assessment**
3. Answer all questions
4. Click **Submit**
5. View results immediately (score, pass/fail, explanations)

If they don't pass, they can retry up to the maximum attempts.

## Step 5: Document Acknowledgment

For documents that require read-and-acknowledge (without a quiz):

1. Navigate to the effective page
2. Click **Require Acknowledgment** in the learning panel
3. Assign users who must acknowledge
4. Users see an **Acknowledge** button on the page
5. Clicking it records the acknowledgment with a timestamp

**API equivalent:**

```
POST /api/v1/learning/acknowledgments
{
  "page_id": "...",
  "user_id": "..."
}
```

## Step 6: Track Completion

Monitor training status from the admin dashboard:

1. Navigate to **Admin** → **Learning** → **Assignments**
2. View completion rates per assessment
3. Filter by status: Pending, In Progress, Completed, Overdue
4. Export training records for compliance audits

### Training Records

Each completion record includes:
- User identity
- Assessment title and linked document
- Score and pass/fail status
- Completion timestamp
- Number of attempts

These records support ISO 9001/13485 training requirements and can be exported for auditor review.

## Next Steps

- [Document Numbering](../how-to/document-numbering.md) — Assign controlled document numbers
- [Compliance Matrix](../reference/compliance-matrix.md) — See which features map to regulatory requirements
