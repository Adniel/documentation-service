# Learning API Reference

Base path: `/api/v1/learning`

## Assessments

### POST /learning/assessments

Create an assessment linked to a page.

**Request:**
```json
{
  "page_id": "page-uuid",
  "title": "SOP-QMS-001 Comprehension Check",
  "description": "Verify understanding of quality management procedures",
  "passing_score": 80,
  "max_attempts": 3
}
```

**Response (201):**
```json
{
  "id": "assessment-uuid",
  "page_id": "page-uuid",
  "title": "SOP-QMS-001 Comprehension Check",
  "passing_score": 80,
  "max_attempts": 3,
  "question_count": 0,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### GET /learning/assessments

List assessments. Supports filtering by `page_id` and `organization_id`.

### GET /learning/assessments/{assessment_id}

Get a single assessment with its questions.

### PUT /learning/assessments/{assessment_id}

Update assessment details.

### DELETE /learning/assessments/{assessment_id}

Delete an assessment.

## Questions

### POST /learning/assessments/{assessment_id}/questions

Add a question to an assessment.

**Request (Multiple Choice):**
```json
{
  "question_text": "What is required before a document can be made effective?",
  "question_type": "multiple_choice",
  "options": [
    { "text": "All required approvals", "is_correct": true },
    { "text": "Author signature only", "is_correct": false },
    { "text": "Manager email", "is_correct": false },
    { "text": "No requirements", "is_correct": false }
  ],
  "explanation": "Per SOP-QMS-001, all signatures defined in the approval matrix must be collected.",
  "sort_order": 1
}
```

**Request (True/False):**
```json
{
  "question_text": "Electronic signatures require re-authentication.",
  "question_type": "true_false",
  "correct_answer": true,
  "explanation": "21 CFR Part 11 requires re-authentication at signature time."
}
```

**Question types:** `multiple_choice`, `true_false`, `open_ended`

### GET /learning/assessments/{assessment_id}/questions

List questions for an assessment.

### PUT /learning/assessments/{assessment_id}/questions/{question_id}

Update a question.

### DELETE /learning/assessments/{assessment_id}/questions/{question_id}

Delete a question.

## Assignments

### POST /learning/assignments

Assign an assessment to users.

**Request:**
```json
{
  "assessment_id": "assessment-uuid",
  "user_ids": ["user-uuid-1", "user-uuid-2"],
  "due_date": "2025-03-01T00:00:00Z"
}
```

**Response (201):**
```json
{
  "assignments": [
    {
      "id": "assignment-uuid-1",
      "assessment_id": "assessment-uuid",
      "user_id": "user-uuid-1",
      "status": "pending",
      "due_date": "2025-03-01T00:00:00Z"
    },
    {
      "id": "assignment-uuid-2",
      "assessment_id": "assessment-uuid",
      "user_id": "user-uuid-2",
      "status": "pending",
      "due_date": "2025-03-01T00:00:00Z"
    }
  ]
}
```

### GET /learning/assignments

List assignments. Supports filtering by `user_id`, `assessment_id`, `status`.

**Assignment statuses:** `pending`, `in_progress`, `completed`, `overdue`

### GET /learning/assignments/{assignment_id}

Get a single assignment with attempt history.

## Attempts

### POST /learning/assignments/{assignment_id}/attempts

Start a quiz attempt.

**Response (201):**
```json
{
  "id": "attempt-uuid",
  "assignment_id": "assignment-uuid",
  "status": "in_progress",
  "started_at": "2025-01-15T10:00:00Z",
  "questions": [
    {
      "id": "question-uuid",
      "question_text": "What is required before...",
      "question_type": "multiple_choice",
      "options": [
        { "id": "opt-1", "text": "All required approvals" },
        { "id": "opt-2", "text": "Author signature only" }
      ]
    }
  ]
}
```

### POST /learning/assignments/{assignment_id}/attempts/{attempt_id}/submit

Submit answers for an attempt.

**Request:**
```json
{
  "answers": [
    { "question_id": "q-uuid-1", "selected_option_id": "opt-1" },
    { "question_id": "q-uuid-2", "answer": true },
    { "question_id": "q-uuid-3", "text_answer": "Explanation here..." }
  ]
}
```

**Response (200):**
```json
{
  "id": "attempt-uuid",
  "status": "completed",
  "score": 90,
  "passed": true,
  "passing_score": 80,
  "completed_at": "2025-01-15T10:05:00Z",
  "results": [
    { "question_id": "q-uuid-1", "correct": true },
    { "question_id": "q-uuid-2", "correct": true },
    { "question_id": "q-uuid-3", "correct": null, "pending_review": true }
  ]
}
```

## Acknowledgments

### POST /learning/acknowledgments

Record that a user has read and acknowledged a document.

**Request:**
```json
{
  "page_id": "page-uuid"
}
```

**Response (201):**
```json
{
  "id": "ack-uuid",
  "page_id": "page-uuid",
  "user_id": "user-uuid",
  "acknowledged_at": "2025-01-15T10:00:00Z"
}
```

### GET /learning/acknowledgments?page_id={page_id}

List acknowledgments for a page.

### GET /learning/acknowledgments?user_id={user_id}

List acknowledgments by a user.
