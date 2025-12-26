# Sprint 9.5: Administrative UI for Compliance Features

## Overview

This sprint implements administrative UI components for features that are currently API-only. These are critical for making the compliance features (Sprints 5-9) usable by non-technical administrators.

**Goal:** Enable administrators to configure assessments, approval workflows, document control, and signature requirements through the UI without API calls.

---

## Gap Analysis

| Feature | User UI | Admin UI | Status |
|---------|---------|----------|--------|
| Quiz Taking | ✅ QuizTaking.tsx | ❌ None | Need Builder |
| E-Signatures | ✅ SignatureDialog.tsx | ❌ None | Need Config |
| Approval Workflow | ✅ DraftWorkflowActions.tsx | ❌ None | Need Matrix |
| Document Control | ⚠️ Status display only | ❌ None | Need Full UI |
| Audit Trail | ✅ AuditViewer.tsx | ✅ Complete | Done |

---

## Deliverables

### 1. Assessment Builder UI (Priority: P0)

**Components to Create:**

#### `AssessmentBuilder.tsx`
Main assessment configuration panel:
- Assessment title, description
- Passing score (0-100%)
- Time limit (optional)
- Max attempts (optional)
- Active/inactive toggle
- Link to page selector

#### `QuestionEditor.tsx`
Individual question editing:
- Question type selector (multiple choice, true/false, fill-in-blank)
- Question text with rich formatting
- Options editor for multiple choice (add/remove/reorder)
- Correct answer selector
- Points value
- Explanation field
- Sort order drag-and-drop

#### `QuestionBank.tsx`
Question management list:
- List all questions with search/filter
- Reorder questions (drag-and-drop)
- Bulk actions (delete, copy)
- Preview question as student sees it

#### `AssessmentList.tsx` (Admin version)
Manage all assessments:
- List assessments with page titles
- Status (active/inactive, question count)
- Quick actions (edit, preview, deactivate)
- Create new assessment button

**API Already Exists:**
- `POST /learning/assessments` - Create assessment
- `PATCH /learning/assessments/{id}` - Update assessment
- `POST /learning/assessments/{id}/questions` - Add question
- `PATCH /learning/questions/{id}` - Update question
- `DELETE /learning/questions/{id}` - Delete question
- `PUT /learning/assessments/{id}/questions/order` - Reorder questions

---

### 2. Document Lifecycle Management UI (Priority: P0)

**Components to Create:**

#### `LifecyclePanel.tsx`
Document lifecycle actions sidebar:
- Current status with visual indicator
- Available transitions based on current state
- Transition buttons with confirmation dialogs
- Required approvals display
- Effective date picker (for scheduling)

State transitions to support:
```
Draft → In Review → Approved → Effective → Obsolete → Archived
                 ↘ Rejected (back to Draft)
```

#### `DocumentMetadataEditor.tsx`
Edit controlled document metadata:
- Document number (SOP-QMS-001 format)
- Revision (A, B, C...) vs Version (1.0, 1.1...)
- Owner and Custodian (user selector)
- Effective date
- Review date (next scheduled review)
- Retention period
- Classification level selector
- Training required toggle + validity months

#### `SupersessionDialog.tsx`
Mark document as superseded:
- Select replacement document
- Reason for supersession
- Effective date
- Notification to affected users

#### `DocumentControlDashboard.tsx`
Admin dashboard for document control:
- Documents by lifecycle state (chart)
- Upcoming reviews (next 30/60/90 days)
- Expired/overdue reviews
- Documents pending approval
- Recently obsoleted documents
- Export to CSV

**API May Need:**
- `POST /documents/{id}/transition` - Move through lifecycle
- `GET /documents/dashboard` - Dashboard statistics

---

### 3. Approval Matrix Configuration (Priority: P1)

**Components to Create:**

#### `ApprovalMatrixEditor.tsx`
Configure approval requirements:
- Approval rules table
- Conditions: by classification, by document type, by space
- Required approvers: by role, specific users, minimum count
- Escalation rules (time-based)
- Add/edit/delete rules

Example rules:
```
If classification = "Confidential" AND type = "SOP"
Then require: 2 approvers with role >= Editor
              1 approver from QA team
              Complete within 5 business days
```

#### `ApprovalRequestPanel.tsx`
Request signatures/approvals:
- Select document version
- Select required signers (based on matrix or manual)
- Set deadline
- Add notes/instructions
- Send request button

#### `PendingApprovalsPanel.tsx`
Approver's queue:
- Documents awaiting my approval
- Time remaining until deadline
- Quick approve/reject actions
- Filter by priority, due date

**API May Need:**
- `POST /approval-matrix/rules` - Create rule
- `GET /approval-matrix` - Get all rules
- `POST /documents/{id}/request-approval` - Request approval from users

---

### 4. Signature Configuration UI (Priority: P1)

**Components to Create:**

#### `SignatureRequirementsEditor.tsx`
Configure signature policies:
- Required meanings per document type
- Required signer roles
- Re-authentication timeout settings
- Legal notice text customization

#### `SignatureRequestDialog.tsx`
Request specific signatures:
- Select document/version
- Select signer(s)
- Select required meaning
- Set deadline
- Optional message

#### `SignatureHistoryPanel.tsx`
Full signature history:
- All signatures on document (valid and invalidated)
- Verification status
- Export for auditors

**API Already Exists:**
- `POST /signatures/initiate` - Initiate signature
- `POST /signatures/complete` - Complete with password
- `GET /pages/{id}/signatures` - List signatures
- `GET /signatures/{id}/verify` - Verify signature

---

### 5. Training Assignment UI (Priority: P1)

**Components to Create:**

#### `AssignTrainingDialog.tsx`
Assign training to users:
- Select document(s) requiring training
- Select user(s) or user groups
- Set due date
- Optional message
- Bulk assign capability

#### `TrainingAdminDashboard.tsx`
Admin training oversight:
- Overall completion rates
- Users with overdue training
- Documents with low completion
- Training validity expiring soon
- Quick actions (send reminder, extend deadline)

**API Already Exists:**
- `POST /learning/assignments` - Create assignment
- `POST /learning/assignments/bulk` - Bulk assign
- `GET /learning/reports/completion` - Completion rates
- `GET /learning/reports/overdue` - Overdue assignments

---

## Implementation Phases

### Phase 1: Assessment Builder (Days 1-3)
| Task | Priority | Est. Lines |
|------|----------|------------|
| AssessmentBuilder.tsx | P0 | 400 |
| QuestionEditor.tsx | P0 | 350 |
| QuestionBank.tsx | P0 | 250 |
| AssessmentList.tsx (admin) | P0 | 200 |
| Integration & testing | P0 | - |

### Phase 2: Document Lifecycle (Days 4-6)
| Task | Priority | Est. Lines |
|------|----------|------------|
| LifecyclePanel.tsx | P0 | 300 |
| DocumentMetadataEditor.tsx | P0 | 400 |
| SupersessionDialog.tsx | P1 | 150 |
| DocumentControlDashboard.tsx | P1 | 350 |
| Backend: transition endpoint | P0 | 150 |

### Phase 3: Approvals & Signatures (Days 7-9)
| Task | Priority | Est. Lines |
|------|----------|------------|
| ApprovalMatrixEditor.tsx | P1 | 400 |
| ApprovalRequestPanel.tsx | P1 | 250 |
| PendingApprovalsPanel.tsx | P1 | 200 |
| SignatureRequestDialog.tsx | P1 | 200 |
| Backend: approval matrix API | P1 | 300 |

### Phase 4: Training Admin (Days 10-11)
| Task | Priority | Est. Lines |
|------|----------|------------|
| AssignTrainingDialog.tsx | P1 | 250 |
| TrainingAdminDashboard.tsx | P1 | 350 |

### Phase 5: Integration & Polish (Days 12-14)
| Task | Priority |
|------|----------|
| Admin navigation/routing | P0 |
| Role-based menu visibility | P0 |
| E2E tests for admin flows | P1 |
| Documentation | P2 |

---

## New Files Summary

### Frontend Components
```
frontend/src/components/
├── learning/
│   ├── AssessmentBuilder.tsx      # NEW
│   ├── QuestionEditor.tsx         # NEW
│   ├── QuestionBank.tsx           # NEW
│   └── AssessmentAdminList.tsx    # NEW
├── document-control/
│   ├── LifecyclePanel.tsx         # NEW
│   ├── DocumentMetadataEditor.tsx # NEW
│   ├── SupersessionDialog.tsx     # NEW
│   └── DocumentControlDashboard.tsx # NEW
├── approval/
│   ├── ApprovalMatrixEditor.tsx   # NEW
│   ├── ApprovalRequestPanel.tsx   # NEW
│   └── PendingApprovalsPanel.tsx  # NEW
├── signatures/
│   ├── SignatureRequestDialog.tsx # NEW
│   └── SignatureHistoryPanel.tsx  # NEW
└── training/
    ├── AssignTrainingDialog.tsx   # NEW
    └── TrainingAdminDashboard.tsx # NEW
```

### Frontend Pages
```
frontend/src/pages/
├── AdminDashboard.tsx             # NEW - Central admin hub
├── AssessmentManagement.tsx       # NEW - Assessment CRUD
├── DocumentControlPage.tsx        # NEW - Lifecycle management
└── ApprovalMatrixPage.tsx         # NEW - Workflow config
```

### Backend (if needed)
```
backend/src/api/endpoints/
├── document_control.py            # ADD: transition endpoint
└── approval_matrix.py             # NEW: matrix CRUD
```

---

## API Additions Required

### Document Control
```python
# Lifecycle transition
POST /api/v1/documents/{id}/transition
{
    "to_status": "approved",
    "effective_date": "2025-01-15",
    "reason": "Annual review completed"
}

# Dashboard stats
GET /api/v1/documents/control/dashboard
Response: {
    "by_status": {"draft": 12, "effective": 45, ...},
    "upcoming_reviews": [...],
    "pending_approvals": [...],
    "recently_obsoleted": [...]
}
```

### Approval Matrix
```python
# Create rule
POST /api/v1/approval-matrix/rules
{
    "name": "Confidential SOP Approval",
    "conditions": {
        "classification": "confidential",
        "document_type": "sop"
    },
    "requirements": {
        "min_approvers": 2,
        "required_roles": ["qa_manager"],
        "deadline_days": 5
    }
}

# Get all rules
GET /api/v1/approval-matrix/rules

# Request approval
POST /api/v1/documents/{id}/request-approval
{
    "approvers": ["user-uuid-1", "user-uuid-2"],
    "deadline": "2025-01-20",
    "message": "Please review by EOD Friday"
}
```

---

## Verification Criteria

### Assessment Builder
- [ ] Admin can create new assessment for any page
- [ ] Admin can add/edit/delete questions of all types
- [ ] Admin can reorder questions via drag-and-drop
- [ ] Admin can preview assessment as student
- [ ] Admin can activate/deactivate assessments

### Document Lifecycle
- [ ] Admin can transition documents through all states
- [ ] System enforces valid transitions only
- [ ] Metadata editor saves all ISO 15489 fields
- [ ] Dashboard shows accurate statistics
- [ ] Supersession correctly links documents

### Approval Workflow
- [ ] Admin can create approval matrix rules
- [ ] System auto-selects approvers based on rules
- [ ] Approvers see pending items in queue
- [ ] Deadlines and escalations work correctly

### Signatures
- [ ] Admin can request signatures from specific users
- [ ] Signature history shows full audit trail
- [ ] Export works for compliance audits

### Training
- [ ] Admin can assign training to users/groups
- [ ] Bulk assignment works correctly
- [ ] Dashboard shows accurate completion data
- [ ] Reminder system works

---

## Dependencies

- Sprint 9 Learning Module (complete)
- Sprint 7 Electronic Signatures (complete)
- Sprint 6 Document Control (complete)
- Sprint 5 Access Control (complete)

## Risks

1. **Approval Matrix Complexity** - May need to simplify rules engine
2. **Drag-and-drop** - Need library (react-beautiful-dnd or dnd-kit)
3. **Role-based visibility** - Need to wire up permission checks in UI

---

## Definition of Done

1. All P0 components implemented and tested
2. Admin can manage assessments end-to-end through UI
3. Admin can manage document lifecycle through UI
4. E2E tests pass for critical admin workflows
5. Documentation updated with admin guide
