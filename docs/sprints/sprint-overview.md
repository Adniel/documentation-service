# Sprint Overview - Documentation Service Platform

## Sprint Plan

Projektet är uppdelat i 12 sprintar. Varje sprint levererar ett körbart system med inkrementell funktionalitet.

## Sprint Dependencies

```
Sprint 1: Foundation ────────────────────────────────────────►
          │
Sprint 2: Editor Core ─────────────────────────────────────►
          │
Sprint 3: Content Organization ────────────────────────────►
          │
Sprint 4: Version Control UI ──────────────────────────────►
          │
Sprint 5: Access Control ──────────────────────────────────►
          │
Sprint 6: Document Control ────────────────────────────────►
          │
Sprint 7: E-Signatures ────────────────────────────────────►
          │
Sprint 8: Audit Trail ─────────────────────────────────────►
          │
Sprint 9: Learning Basics ─────────────────────────────────►
          │
Sprint 10: AI Features ────────────────────────────────────►
          │
Sprint 11: MCP Integration ────────────────────────────────►
          │
Sprint 12: Publishing & Polish ────────────────────────────►
```

## MVP Milestones

### MVP 1: Basic Documentation (Sprint 1-4)
- Användare kan skapa och redigera dokument
- Block-baserad editor med grundläggande block
- Content-hierarki och navigation
- Version control med diff och historik

### MVP 2: Document Control (Sprint 5-8)
- Rollbaserad åtkomstkontroll
- Godkännandeflöden
- Elektroniska signaturer (21 CFR Part 11)
- Komplett audit trail

### MVP 3: Learning & AI (Sprint 9-11)
- Assessment och acknowledgment
- AI-genererade frågor
- MCP-integration för externa konsumenter
- AI writing assistant

### MVP 4: Publishing (Sprint 12)
- Publicerade sites
- Theming och customization
- Analytics
- Performance-optimering

## Sprint Summary

| Sprint | Fokus | Huvudleverabler |
|--------|-------|-----------------|
| 1 | Foundation | API, Auth, Git integration, DB |
| 2 | Editor Core | Block editor, Markdown support |
| 3 | Content Organization | Hierarchy, Navigation, Search |
| 4 | Version Control UI | Change requests, Diff, History |
| 5 | Access Control | Permissions, Classifications, ACLs |
| 6 | Document Control | Lifecycle, Numbering, Metadata, Retention |
| 7 | E-Signatures | 21 CFR Part 11 compliant signatures |
| 8 | Audit Trail | Immutable logging, Hash chain, Tamper detection |
| 9 | Learning Basics | Assessment, Acknowledgment |
| 10 | AI Features | Question gen, Masking |
| 11 | MCP Integration | Server & Client |
| 12 | Publishing | Sites, Themes, Analytics |

---

## Regulatory Compliance Scope

This platform targets compliance with:
- **FDA 21 CFR Part 11** - Electronic Records and Electronic Signatures
- **ISO 9001:2015** - Quality Management Systems (§7.5 Documented Information)
- **ISO 13485:2016** - Medical Devices Quality Management (§4.2 Document Control)
- **ISO 15489** - Records Management
- **EU Annex 11** - Computerised Systems (GxP)

**CRITICAL**: Sprints 5-8 contain compliance-critical features. These sprints MUST be implemented according to the detailed requirements below to achieve regulatory compliance.

## Testing Requirements

Varje sprint MÅSTE inkludera tester som verifierar implementationen. Tester är inte valfria.

### Test Infrastructure

**Backend (pytest)**
- Konfiguration: `backend/pyproject.toml`
- Testfiler: `backend/tests/`
- Kör: `cd backend && pytest`
- Coverage: `pytest --cov=src --cov-report=html`

**Frontend (Vitest)**
- Konfiguration: `frontend/vitest.config.ts`
- Testfiler: `frontend/src/**/*.test.{ts,tsx}`
- Kör: `cd frontend && npm test`
- Coverage: `npm run test:coverage`

### Per-Sprint Test Krav

| Sprint | Backend Tests | Frontend Tests | Compliance Tests |
|--------|--------------|----------------|------------------|
| 1 | Auth, JWT, Password hashing, Git service | - | - |
| 2 | - | Markdown utils, Editor hooks | - |
| 3 | Search service, Navigation service | SearchBar, Breadcrumbs, Diátaxis | - |
| 4 | Branch/merge operations, Diff | DiffViewer, HistoryTimeline | - |
| 5 | Permission service, ACL inheritance | PermissionGuard, RoleSelector | Session timeout, Access denial logging |
| 6 | Document numbering, Revision service, Metadata validation | WorkflowStatus, ApprovalPanel, MetadataForm | Numbering uniqueness, Retention enforcement |
| 7 | E-signature service, Re-auth, Hash verification | SignatureDialog, SignatureList | 21 CFR Part 11 compliance suite |
| 8 | Audit service, Hash chain, Event integrity | AuditLog, ComplianceReport | Chain integrity, Immutability |
| 9 | Assessment service, Quiz engine | QuizFlow, QuestionCard | Training record retention |
| 10 | AI service integration | WritingAssistant, QuestionGenerator | - |
| 11 | MCP protocol handlers | MCPConnectionStatus | Service account audit |
| 12 | Publishing service, Theme engine | ThemePreview, PublishDialog | - |

### Test Coverage Targets

- **Unit tests**: >= 80% coverage för business logic
- **Integration tests**: Alla API endpoints
- **E2E tests**: Kritiska workflows (Sprint 6+)
- **Compliance tests**:
  - Sprint 5+: Access control and audit logging
  - Sprint 6+: Document lifecycle and metadata validation
  - Sprint 7+: 21 CFR Part 11 signature compliance
  - Sprint 8+: Audit trail integrity verification

### Compliance Test Categories

| Category | Description | Required From |
|----------|-------------|---------------|
| **Access Control** | Permission enforcement, session management, denial logging | Sprint 5 |
| **Document Control** | Numbering uniqueness, revision tracking, metadata validation | Sprint 6 |
| **Electronic Signatures** | Re-auth, timestamp, hash linking, meaning capture | Sprint 7 |
| **Audit Trail** | Chain integrity, immutability, reason capture | Sprint 8 |
| **Regulatory Reports** | Export functionality, compliance dashboards | Sprint 8 |

### Validering

Innan en sprint anses klar:
1. Alla tester måste passera (`pytest` / `npm test`)
2. Inga TypeScript-fel (`npm run type-check`)
3. Inga lint-fel (`npm run lint`)
4. Coverage-mål uppfyllda

## Per-Sprint Runnable State

### After Sprint 1
- API running with health check
- User can register/login
- Git repo can be created programmatically
- Basic database schema

### After Sprint 2
- Working block-based editor
- Documents can be created and edited
- Markdown import/export
- Auto-save to Git

### After Sprint 3
- Full content hierarchy (Org → Workspace → Space → Page)
- Sidebar navigation
- Full-text search
- Diátaxis tagging

### After Sprint 4
- Create "drafts" (branches)
- Visual diff viewer
- Version history timeline
- Merge/publish workflow

### After Sprint 5
- Role-based permissions (Owner → Viewer)
- Document classification (Public → Restricted)
- Permission inheritance with document-level overrides
- Granular permission model (Permission table)
- Permission change audit logging
- Session timeout enforcement
- Access denied handling with audit logging

### After Sprint 6
- Document lifecycle (Draft → In Review → Approved → Effective → Obsolete)
- Auto-numbering service with configurable schemes (e.g., SOP-QMS-001)
- Document type classification (SOP, WI, Form, Policy, Record)
- Revision tracking separate from version (Rev A, Rev B)
- Effective/approved/review dates tracking
- Owner and custodian assignment
- Retention policy fields (period, disposition date, method)
- Supersession tracking (links to replaced documents)
- Approval workflows with reviewer assignment
- Periodic review reminders and next review dates

### After Sprint 7
- 21 CFR Part 11 compliant e-signatures:
  - ElectronicSignature model with signer info frozen at signature time
  - Signature meaning capture (Authored, Reviewed, Approved, Witnessed, Acknowledged)
  - Re-authentication service (password re-entry + optional MFA)
  - Trusted timestamp from NTP service
  - Content hash (SHA-256) linking signature to exact content
  - Git commit SHA linkage for non-repudiation
  - Signature verification endpoint
- **Two Signing Scenarios:**
  - **Collective Signing** (SigningCeremony): Multiple signers on same document (e.g., board protocol)
  - **Individual Signing** (integrated with Sprint 9): Per-user acknowledgment (e.g., Code of Conduct)
- SigningCeremony with configurable completion rules (all/count/percentage)
- SigningRequest per signer with status tracking
- Peer review (4-eyes principle): signers can request colleague review before signing
- Delegation support: configurable per ceremony with full audit trail
- Reminders and timeout behavior (pending/silent-decline/silent-approval)
- Approval matrix enforcement
- Signature manifestation display (name, date/time, meaning)

### After Sprint 8
- Append-only audit trail with database-level immutability protection
- Cryptographic hash chain:
  - AuditService with hash chain calculation
  - Each event links to previous event hash
  - SHA-256 content hashing
  - Chain integrity verification endpoint
  - Tamper detection mechanism
- Mandatory reason capture for critical operations
- NTP-validated timestamps
- Compliance reports (who, what, when, why)
- Export functionality (CSV, PDF for auditors)
- Database trigger preventing UPDATE/DELETE on audit_events

### After Sprint 9
- **Mass Acknowledgment Campaigns:**
  - AcknowledgmentCampaign model for sending documents to many recipients
  - Assignment model linking users to documents with status tracking
  - Integration with ElectronicSignature (meaning=ACKNOWLEDGED)
- **Assessment Integration (Optional):**
  - Optional quiz requirement before signing (default: disabled)
  - Manual questions embedded in documents
  - Pass criteria configuration (count, percentage, attempts)
  - Assessment attempt tracking
- Assignment dashboard for users ("Action Required" items)
- Campaign management for admins
- Completion reports and compliance tracking
- Due date management with reminders

### After Sprint 10
- AI-generated questions
- Writing assistant
- Document masking (redaction)
- Multi-source support

### After Sprint 11
- Platform as MCP server
- External AI agents can query
- Service account management
- Rate limiting and audit

### After Sprint 12
- Published documentation sites
- Custom domains
- Theming
- Analytics dashboard
- Performance optimized

## Technology Decision Required

Before starting Sprint 1, technology decisions must be made:

1. **Backend framework** - Node.js, Python, Go, or Rust
2. **Frontend framework** - React, Vue, or Svelte
3. **Editor library** - TipTap, Slate, or Lexical
4. **Search engine** - Meilisearch or Elasticsearch
5. **AI provider** - OpenAI, Anthropic, or self-hosted

Use `/docservice:tech-decision` to make and document these choices.

## Getting Started

1. Run `/docservice:tech-decision` to choose technologies
2. Run `/docservice:sprint 1` for Sprint 1 details
3. Follow the implementation guide
4. Run tests to verify
5. Move to next sprint

---

## Detailed Sprint Requirements

### Sprint 4: Version Control UI

**Overview:**
Sprint 4 exposes Git functionality to users through an abstracted UI. Users work with "drafts" and "change requests" without seeing Git concepts. The system translates user actions into Git operations behind the scenes.

**Key Principle: Git Abstraction**
| User Concept | Git Operation | User Sees |
|--------------|---------------|-----------|
| Create draft | `git checkout -b draft/CR-xxx` | "Draft created" |
| Save changes | `git commit` | Auto-save indicator |
| View history | `git log` | Version timeline |
| Compare versions | `git diff` | Side-by-side diff |
| Submit for review | DB record update | "Submitted for review" |
| Publish | `git merge --no-ff` | "Published" |

**ChangeRequest Model (src/db/models/change_request.py):**

```python
class ChangeRequestStatus(str, Enum):
    DRAFT = "draft"              # Work in progress
    SUBMITTED = "submitted"      # Submitted for review
    IN_REVIEW = "in_review"      # Being reviewed
    CHANGES_REQUESTED = "changes_requested"  # Reviewer requested changes
    APPROVED = "approved"        # Approved, ready to publish
    PUBLISHED = "published"      # Merged to main
    REJECTED = "rejected"        # Rejected by reviewer
    CANCELLED = "cancelled"      # Cancelled by author

class ChangeRequest(Base, UUIDMixin, TimestampMixin):
    """Application-level tracking of document drafts (Git branches)."""

    # Document being edited
    page_id: Mapped[UUID]                      # FK to pages

    # Change request metadata
    title: Mapped[str]                         # "Update safety procedures"
    description: Mapped[str | None]            # Longer explanation

    # Author
    author_id: Mapped[UUID]                    # FK to users

    # Git tracking (hidden from user)
    branch_name: Mapped[str]                   # "draft/CR-001-safety-update"
    base_commit_sha: Mapped[str]               # Commit when draft started
    head_commit_sha: Mapped[str | None]        # Latest commit on branch

    # Status
    status: Mapped[ChangeRequestStatus] = ChangeRequestStatus.DRAFT

    # Review tracking
    submitted_at: Mapped[datetime | None]
    reviewer_id: Mapped[UUID | None]           # Assigned reviewer
    reviewed_at: Mapped[datetime | None]
    review_comment: Mapped[str | None]

    # Publication
    published_at: Mapped[datetime | None]
    published_by_id: Mapped[UUID | None]
    merge_commit_sha: Mapped[str | None]       # Commit after merge

    # Relationships
    page: Mapped["Page"] = relationship()
    author: Mapped["User"] = relationship(foreign_keys=[author_id])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewer_id])
    comments: Mapped[list["ChangeRequestComment"]] = relationship()


class ChangeRequestComment(Base, UUIDMixin, TimestampMixin):
    """Comments/discussion on a change request."""

    change_request_id: Mapped[UUID]            # FK to change_requests
    author_id: Mapped[UUID]                    # FK to users
    content: Mapped[str]                       # Markdown content

    # Optional: line-level comment
    file_path: Mapped[str | None]
    line_number: Mapped[int | None]

    # Thread support
    parent_id: Mapped[UUID | None]             # For replies
```

**Services Required:**

```python
# ChangeRequestService (src/modules/content/change_request_service.py)
class ChangeRequestService:
    async def create_draft(
        self,
        page_id: UUID,
        author_id: UUID,
        title: str,
        description: str | None = None,
    ) -> ChangeRequest:
        """
        Create a new draft for editing a page.

        Steps:
        1. Get current page and its git_commit_sha
        2. Generate branch name: draft/CR-{number}-{slug}
        3. Call git_service.create_branch(branch_name, base_sha)
        4. Create ChangeRequest record with status=DRAFT
        5. Log audit event
        """

    async def save_draft(
        self,
        change_request_id: UUID,
        content: dict,
        author_id: UUID,
    ) -> ChangeRequest:
        """
        Save changes to a draft (auto-save).

        Steps:
        1. Switch to draft branch
        2. Update content file
        3. Commit with auto-generated message
        4. Update head_commit_sha
        """

    async def submit_for_review(
        self,
        change_request_id: UUID,
        reviewer_id: UUID | None = None,
    ) -> ChangeRequest:
        """Submit draft for review."""

    async def approve(
        self,
        change_request_id: UUID,
        reviewer_id: UUID,
        comment: str | None = None,
    ) -> ChangeRequest:
        """Approve change request."""

    async def request_changes(
        self,
        change_request_id: UUID,
        reviewer_id: UUID,
        comment: str,
    ) -> ChangeRequest:
        """Request changes from author."""

    async def publish(
        self,
        change_request_id: UUID,
        publisher_id: UUID,
    ) -> ChangeRequest:
        """
        Publish approved changes.

        Steps:
        1. Verify status is APPROVED
        2. Call git_service.merge_branch(draft_branch, main)
        3. Update page.git_commit_sha with merge commit
        4. Update status to PUBLISHED
        5. Clean up branch (optional)
        6. Log audit event
        """


# DiffService (src/modules/content/diff_service.py)
class DiffService:
    async def get_diff(
        self,
        page_id: UUID,
        from_sha: str,
        to_sha: str,
    ) -> DiffResult:
        """
        Generate diff between two versions.

        Returns:
        - hunks: list of changes with context
        - additions: line count
        - deletions: line count
        - files_changed: count
        """

    async def get_change_request_diff(
        self,
        change_request_id: UUID,
    ) -> DiffResult:
        """Get diff between draft and base (what changed in this CR)."""
```

**API Endpoints:**

```
# Change Requests (Drafts)
POST   /api/v1/pages/{page_id}/drafts              - Create new draft
GET    /api/v1/pages/{page_id}/drafts              - List drafts for page
GET    /api/v1/drafts/{id}                         - Get draft details
PATCH  /api/v1/drafts/{id}                         - Update draft content
DELETE /api/v1/drafts/{id}                         - Cancel/delete draft

# Workflow
POST   /api/v1/drafts/{id}/submit                  - Submit for review
POST   /api/v1/drafts/{id}/approve                 - Approve draft
POST   /api/v1/drafts/{id}/request-changes         - Request changes
POST   /api/v1/drafts/{id}/publish                 - Publish (merge)

# History & Diff
GET    /api/v1/pages/{page_id}/history             - Version history (exists)
GET    /api/v1/pages/{page_id}/diff                - Compare two versions
GET    /api/v1/drafts/{id}/diff                    - Draft vs published diff

# Comments
POST   /api/v1/drafts/{id}/comments                - Add comment
GET    /api/v1/drafts/{id}/comments                - List comments
```

**Frontend Components:**

```typescript
// HistoryTimeline.tsx - Visual version history
interface HistoryTimelineProps {
  pageId: string;
  onVersionSelect: (sha: string) => void;
}

// Features:
// - Vertical timeline with commits
// - Author avatars and names
// - Commit messages
// - Timestamps (relative: "2 hours ago")
// - Click to view version
// - Compare button between versions

// DiffViewer.tsx - Side-by-side diff comparison
interface DiffViewerProps {
  pageId: string;
  fromSha: string;
  toSha: string;
}

// Features:
// - Side-by-side or unified view toggle
// - Syntax highlighting for code blocks
// - Line numbers
// - Additions (green) / Deletions (red)
// - Context lines (collapsible)
// - Navigate between hunks

// DraftEditor.tsx - Edit within a draft context
interface DraftEditorProps {
  changeRequestId: string;
}

// Features:
// - Shows draft status badge
// - Auto-save to draft branch
// - "Submit for Review" button
// - Shows diff from published version

// DraftList.tsx - List and manage drafts
interface DraftListProps {
  pageId: string;
}

// Features:
// - List all drafts for a page
// - Status badges (Draft, In Review, Approved)
// - Author and reviewer info
// - Actions: Edit, Submit, Cancel
// - Filter by status

// PublishWorkflow.tsx - Review and publish flow
interface PublishWorkflowProps {
  changeRequestId: string;
}

// Features:
// - Review checklist
// - Approve / Request Changes buttons
// - Comment thread
// - Publish button (for approved)
// - Conflict resolution (if needed)
```

**Frontend Routes:**

```typescript
// Add to router
/pages/:pageId/history           - HistoryPage (timeline view)
/pages/:pageId/diff              - DiffPage (compare versions)
/pages/:pageId/drafts            - DraftListPage
/pages/:pageId/drafts/new        - Create new draft
/drafts/:draftId                 - View/edit draft
/drafts/:draftId/review          - Review workflow
```

**Tests Required:**
- Unit: ChangeRequest status transitions
- Unit: Branch name generation
- Unit: Diff generation
- Integration: Create draft → edit → submit → approve → publish flow
- Integration: Conflict detection on merge
- E2E: Full draft workflow in browser
- E2E: History timeline navigation
- E2E: Diff viewer functionality

---

### Sprint 5: Access Control (ISO 9001 §7.5.3, 21 CFR §11.10(d))

**Regulatory Requirements:**
- ISO 9001 §7.5.3.1: Control access to documented information
- ISO 13485 §4.2.4: Appropriate authorization for document access
- 21 CFR §11.10(d): Limiting system access to authorized individuals

**Database Models:**

```python
# Permission model (src/db/models/permission.py)
class Role(str, Enum):
    OWNER = "owner"          # Full control
    ADMIN = "admin"          # Manage members, settings
    EDITOR = "editor"        # Create, edit, delete content
    REVIEWER = "reviewer"    # Review, comment, approve
    VIEWER = "viewer"        # Read-only access

class PermissionScope(str, Enum):
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    SPACE = "space"
    DOCUMENT = "document"    # Override

class Permission(Base, UUIDMixin, TimestampMixin):
    user_id: UUID                    # User granted permission
    scope: PermissionScope           # Level of permission
    organization_id: UUID | None     # Scope target
    workspace_id: UUID | None
    space_id: UUID | None
    document_id: UUID | None         # Document-level override
    role: Role                       # Permission level
    granted_by_id: UUID              # Who granted (for audit)
```

**Services Required:**
1. `PermissionService` - Check, grant, revoke permissions
2. `PermissionInheritanceService` - Resolve effective permissions through hierarchy
3. `SessionService` - Session timeout enforcement (configurable, default 30 min)

**API Endpoints:**
- `GET /api/v1/permissions/{resource_type}/{resource_id}` - List permissions
- `POST /api/v1/permissions` - Grant permission (logged to audit)
- `DELETE /api/v1/permissions/{id}` - Revoke permission (logged to audit)
- `GET /api/v1/permissions/effective/{resource_type}/{resource_id}` - Resolved permissions

**Tests Required:**
- Unit: Permission inheritance resolution
- Unit: Role capability mapping
- Integration: Permission CRUD with audit logging
- Integration: Access denial logging
- Compliance: Session timeout enforcement

---

### Sprint 6: Document Control (ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489)

**Regulatory Requirements:**
- ISO 9001 §7.5.2: Documents must be approved before release
- ISO 13485 §4.2.4: Unique document identification required
- ISO 13485 §4.2.5: Changes must be identified and controlled
- ISO 15489: Records management requirements

**Page Model Additions (src/db/models/page.py):**

```python
# Document Control Fields
document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Enum: SOP, WI, FORM, POLICY, RECORD, SPECIFICATION, MANUAL
document_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # Auto-generated, format configurable per org (e.g., "SOP-QMS-001")
revision: Mapped[str] = mapped_column(String(20), nullable=False, default="A")
    # Letter-based: A, B, C... or numeric based on org preference
major_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
minor_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

# Date Tracking (ISO 9001 §7.5.2)
approved_date: Mapped[datetime | None]      # When approved
effective_date: Mapped[datetime | None]     # When becomes active
review_due_date: Mapped[datetime | None]    # Periodic review deadline
next_review_date: Mapped[datetime | None]   # Scheduled next review
reviewed_date: Mapped[datetime | None]      # Last review date
reviewed_by_id: Mapped[UUID | None]         # Who performed review

# Ownership (ISO 13485 §4.2.4)
owner_id: Mapped[UUID]                      # Document owner (required)
custodian_id: Mapped[UUID | None]           # Document custodian

# Retention (ISO 15489)
retention_period_years: Mapped[int | None]  # How long to keep
disposition_date: Mapped[datetime | None]   # When to dispose
disposition_method: Mapped[str | None]      # "archive" | "destroy"

# Supersession (ISO 13485 §4.2.4)
supersedes_id: Mapped[UUID | None]          # FK to replaced document

# Change Control (ISO 13485 §4.2.5)
change_summary: Mapped[str | None]          # Brief change description
change_reason: Mapped[str | None]           # Why changed (required for major revisions)

# Training Requirement
requires_training: Mapped[bool] = mapped_column(default=False)
training_validity_months: Mapped[int | None]
```

**New Models:**

```python
# DocumentNumberSequence (src/db/models/document_number.py)
class DocumentNumberSequence(Base, UUIDMixin):
    organization_id: UUID
    document_type: str
    prefix: str                    # e.g., "SOP-QMS"
    current_number: int            # Auto-incrementing
    format_pattern: str            # e.g., "{prefix}-{number:03d}"

# DocumentRelation (for traceability)
class DocumentRelation(Base, UUIDMixin):
    source_document_id: UUID
    target_document_id: UUID
    relation_type: str             # "references", "implements", "derives_from"
```

**Services Required:**
1. `DocumentNumberingService` - Auto-generate unique document numbers
2. `RevisionService` - Manage revision increments and history
3. `RetentionService` - Track and enforce retention policies
4. `ReviewReminderService` - Schedule and send review reminders
5. `DocumentMetadataService` - Validate required metadata on status transitions

**Validation Rules:**
- Document number MUST be generated before first save
- Effective date MUST be >= Approved date
- Review due date MUST be set when status = "effective"
- Change reason REQUIRED when major_version increments
- Owner REQUIRED for all controlled documents
- Retention period REQUIRED for document types: RECORD, FORM

**API Endpoints:**
- `POST /api/v1/documents/number/generate` - Generate next document number
- `GET /api/v1/documents/{id}/revisions` - List all revisions
- `POST /api/v1/documents/{id}/revise` - Create new revision
- `GET /api/v1/documents/review-due` - Documents due for review
- `GET /api/v1/documents/retention-due` - Documents due for disposition

**Tests Required:**
- Unit: Document number generation (uniqueness, format)
- Unit: Revision increment logic
- Unit: Metadata validation on transitions
- Integration: Full lifecycle (Draft → Effective → Obsolete)
- Compliance: Retention policy enforcement

---

### Sprint 7: Electronic Signatures (21 CFR Part 11)

**Regulatory Requirements:**
- 21 CFR §11.50: Signature manifestation (name, date/time, meaning)
- 21 CFR §11.70: Signature must be linked to electronic record
- 21 CFR §11.100: Signature uniqueness and verification
- 21 CFR §11.200: Re-authentication at signing

**ElectronicSignature Model (src/db/models/signature.py):**

```python
class SignatureMeaning(str, Enum):
    AUTHORED = "authored"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    WITNESSED = "witnessed"
    ACKNOWLEDGED = "acknowledged"

class ElectronicSignature(Base, UUIDMixin):
    # Signer Information (frozen at signature time - §11.50)
    signer_id: Mapped[UUID]                    # FK to users
    signer_full_name: Mapped[str]              # Frozen copy
    signer_title: Mapped[str | None]           # Frozen copy
    signer_email: Mapped[str]                  # Frozen copy

    # Signature Meaning (§11.50(a))
    meaning: Mapped[SignatureMeaning]          # REQUIRED

    # Timestamp (§11.50(b)) - MUST be from NTP
    signed_at: Mapped[datetime]                # Timezone-aware
    timestamp_source: Mapped[str]              # NTP server used

    # Content Linkage (§11.70)
    document_id: Mapped[UUID]                  # FK to pages
    git_commit_sha: Mapped[str]                # Exact commit signed
    content_hash: Mapped[str]                  # SHA-256 of signed content

    # Authentication Evidence (§11.200)
    authentication_method: Mapped[str]         # "password", "password+mfa"
    auth_timestamp: Mapped[datetime]           # When re-authenticated
    ip_address: Mapped[str | None]
    user_agent: Mapped[str | None]

    # Optional
    reason: Mapped[str | None]                 # Signer's comment
    workflow_step_id: Mapped[UUID | None]      # If part of workflow

    # Context Links (for two signing scenarios)
    ceremony_id: Mapped[UUID | None]           # For collective signing
    assignment_id: Mapped[UUID | None]         # For individual acknowledgment
```

**SigningCeremony Model (src/db/models/signing_ceremony.py) - Collective Signing:**

```python
class CompletionRule(str, Enum):
    ALL = "all"                    # All signers must sign
    COUNT = "count"                # Specific number required
    PERCENTAGE = "percentage"      # Percentage required

class ExpirationBehavior(str, Enum):
    PENDING = "pending"            # Remain pending until responded (default)
    SILENT_DECLINE = "silent_decline"  # Treat as declined after timeout
    SILENT_APPROVAL = "silent_approval" # Treat as approved after timeout

class SigningCeremony(Base, UUIDMixin, TimestampMixin):
    """Collective signing session for a document (e.g., board protocol)."""

    # Document (frozen at ceremony creation)
    document_id: Mapped[UUID]                  # FK to pages
    git_commit_sha: Mapped[str]                # Frozen content version
    content_hash: Mapped[str]                  # SHA-256 - all sign same content

    # Ceremony metadata
    name: Mapped[str]                          # "Board Protocol 2025-001 Approval"
    ceremony_type: Mapped[str]                 # "approval_matrix", "board_resolution", "contract"
    created_by_id: Mapped[UUID]

    # Signing configuration
    signing_order: Mapped[str]                 # "sequential" | "parallel"
    completion_rule: Mapped[CompletionRule] = CompletionRule.ALL
    required_count: Mapped[int | None]         # For COUNT rule
    required_percentage: Mapped[int | None]    # For PERCENTAGE rule (0-100)

    # Delegation & Peer Review (global settings)
    allow_delegation: Mapped[bool] = False
    allow_peer_review: Mapped[bool] = False
    require_peer_review: Mapped[bool] = False  # All signers MUST get peer review

    # Reminder configuration
    reminder_enabled: Mapped[bool] = True
    reminder_interval_hours: Mapped[int] = 24
    reminder_max_count: Mapped[int | None] = 3

    # Timeout configuration
    timeout_hours: Mapped[int | None] = None
    expiration_behavior: Mapped[ExpirationBehavior] = ExpirationBehavior.PENDING

    # Status
    status: Mapped[str]                        # "pending", "in_progress", "completed", "cancelled"
    completed_at: Mapped[datetime | None]

    # Relationships
    signing_requests: Mapped[list["SigningRequest"]] = relationship()


class SigningRequest(Base, UUIDMixin, TimestampMixin):
    """Individual signing request within a ceremony."""

    ceremony_id: Mapped[UUID]                  # FK to signing_ceremonies
    signer_id: Mapped[UUID]                    # FK to users

    # Role in ceremony
    signer_role: Mapped[str]                   # "chair", "member", "secretary", "witness"
    required_meaning: Mapped[SignatureMeaning] # APPROVED, WITNESSED, etc.
    signing_order: Mapped[int]                 # For sequential signing

    # Status
    status: Mapped[str]                        # "pending", "ready", "signed", "declined"
    notified_at: Mapped[datetime | None]

    # Signature link (created on signing)
    signature_id: Mapped[UUID | None]          # FK to electronic_signatures
    declined_reason: Mapped[str | None]        # If declined

    # Delegation tracking
    delegated_to_id: Mapped[UUID | None]
    delegated_at: Mapped[datetime | None]
    delegation_reason: Mapped[str | None]

    # Peer review tracking (4-eyes principle)
    peer_reviewer_id: Mapped[UUID | None]
    peer_review_requested_at: Mapped[datetime | None]
    peer_review_status: Mapped[str | None]     # "pending", "approved", "dissuaded"
    peer_review_comment: Mapped[str | None]
    peer_reviewed_at: Mapped[datetime | None]

    # Reminder tracking
    last_reminder_sent_at: Mapped[datetime | None]
    reminder_count: Mapped[int] = 0
    timed_out_at: Mapped[datetime | None]
    timeout_action_taken: Mapped[str | None]
```

**Services Required:**

```python
# SignatureService (src/modules/signatures/service.py)
class SignatureService:
    async def create_signature(
        self,
        user: User,
        document_id: UUID,
        meaning: SignatureMeaning,
        password: str,              # Re-authentication
        mfa_code: str | None,       # Optional MFA
        reason: str | None,
    ) -> ElectronicSignature:
        """
        Create 21 CFR Part 11 compliant electronic signature.

        Steps:
        1. Re-authenticate user (verify password + optional MFA)
        2. Get document and current git commit SHA
        3. Calculate SHA-256 hash of document content
        4. Get trusted timestamp from NTP service
        5. Freeze signer information
        6. Create signature record
        7. Log to audit trail
        """

    async def verify_signature(
        self,
        signature_id: UUID,
    ) -> SignatureVerificationResult:
        """
        Verify signature integrity.

        Checks:
        1. Content hash matches current document at commit SHA
        2. Signer still exists in system
        3. Signature chain is intact
        """

# TrustedTimestampService (src/modules/signatures/timestamp.py)
class TrustedTimestampService:
    """NTP-based trusted timestamp service."""

    def __init__(self, ntp_servers: list[str]):
        self.ntp_servers = ntp_servers  # Multiple for redundancy

    async def get_trusted_timestamp(self) -> datetime:
        """Get timestamp from NTP with validation."""

    async def verify_system_clock(self) -> ClockStatus:
        """Check if system clock is synchronized."""

# ContentHashService (src/modules/signatures/hash.py)
class ContentHashService:
    def calculate_hash(self, content: dict) -> str:
        """Calculate SHA-256 of document content."""
        canonical = json.dumps(content, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
```

**Re-Authentication Endpoint:**

```python
@router.post("/auth/re-authenticate")
async def re_authenticate(
    credentials: ReAuthRequest,
    current_user: CurrentUser,
) -> ReAuthToken:
    """
    Re-authenticate user for signing operation.

    - Verify password matches current user
    - Optionally verify MFA code
    - Return short-lived token (5 min) for signature operation
    """
```

**API Endpoints:**
- `POST /api/v1/auth/re-authenticate` - Re-authenticate for signing
- `POST /api/v1/signatures` - Create signature (requires re-auth token)
- `GET /api/v1/signatures/{id}` - Get signature details
- `GET /api/v1/documents/{id}/signatures` - List document signatures
- `POST /api/v1/signatures/{id}/verify` - Verify signature integrity

**Tests Required:**
- Unit: Content hash calculation (deterministic)
- Unit: Re-authentication flow
- Integration: Full signature creation flow
- Integration: Signature verification
- Compliance: Timestamp from NTP (mock NTP in tests)
- Compliance: Signature immutability
- Security: Re-auth token expiration

---

### Sprint 8: Audit Trail (21 CFR §11.10(e), ISO 9001 §7.5.3)

**Regulatory Requirements:**
- 21 CFR §11.10(e): Audit trail must be secure, computer-generated, timestamped
- 21 CFR §11.10(e): Must record who, what, when, and why
- 21 CFR §11.10(e): Audit trail must be available for review
- ISO 9001 §7.5.3: Records must be legible, identifiable, and retrievable

**AuditService Implementation (src/modules/audit/service.py):**

```python
class AuditService:
    """Service for creating tamper-evident audit trail entries."""

    async def log_event(
        self,
        event_type: AuditEventType,
        actor_id: UUID | None,
        actor_email: str | None,
        resource_type: str | None,
        resource_id: UUID | None,
        resource_name: str | None,
        details: dict[str, Any] | None,
        reason: str | None,           # REQUIRED for critical operations
        actor_ip: str | None = None,
        actor_user_agent: str | None = None,
    ) -> AuditEvent:
        """
        Create immutable audit event with cryptographic chaining.

        Steps:
        1. Get hash of previous event (chain linkage)
        2. Get trusted timestamp
        3. Create event with all metadata
        4. Calculate SHA-256 hash of this event
        5. Store (append-only)
        """

    def _calculate_event_hash(self, event: AuditEvent) -> str:
        """
        Calculate hash for chain integrity.

        Hash includes:
        - event_type
        - timestamp
        - actor_id, actor_email
        - resource_type, resource_id
        - details (including reason)
        - previous_hash
        """
        hash_input = {
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "actor_id": str(event.actor_id),
            "actor_email": event.actor_email,
            "resource_type": event.resource_type,
            "resource_id": str(event.resource_id),
            "details": event.details,
            "previous_hash": event.previous_hash,
        }
        canonical = json.dumps(hash_input, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    async def verify_chain_integrity(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> ChainVerificationResult:
        """
        Verify entire audit chain has not been tampered with.

        Returns:
        - is_valid: bool
        - errors: list of detected issues
        - events_checked: count
        """

    async def export_audit_trail(
        self,
        format: Literal["csv", "json", "pdf"],
        filters: AuditExportFilters,
    ) -> bytes:
        """Export audit trail for external review."""
```

**Database Immutability (Alembic migration):**

```sql
-- Create trigger to prevent modifications
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'Audit trail records cannot be modified';
    ELSIF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Audit trail records cannot be deleted';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_events_immutable
    BEFORE UPDATE OR DELETE ON audit_events
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- Also prevent TRUNCATE
REVOKE TRUNCATE ON audit_events FROM PUBLIC;
```

**Events Requiring Reason (details.reason REQUIRED):**
- `CONTENT_UPDATED` - Why was document changed?
- `CONTENT_DELETED` - Why was document removed?
- `WORKFLOW_REJECTED` - Why was approval rejected?
- `ACCESS_REVOKED` - Why was access removed?
- `SIGNATURE_CREATED` - Signer's comment (optional but recommended)

**API Endpoints:**
- `GET /api/v1/audit/events` - Query audit events (with filters)
- `GET /api/v1/audit/events/{resource_type}/{resource_id}` - Events for resource
- `GET /api/v1/audit/verify` - Verify chain integrity
- `POST /api/v1/audit/export` - Export audit trail

**Tests Required:**
- Unit: Hash chain calculation
- Unit: Event hash verification
- Integration: Audit event creation flow
- Integration: Chain integrity verification
- Compliance: Immutability enforcement (test UPDATE/DELETE blocked)
- Compliance: Reason capture for critical events
- Compliance: Export formats

---

### Sprint 9: Learning & Acknowledgment (Individual Signing Scenario)

**Overview:**
Sprint 9 implements the "Individual Signing" scenario where the same document is sent to many recipients for acknowledgment (e.g., Code of Conduct to all employees). This integrates with Sprint 7 e-signatures and the learning/assessment module.

**AcknowledgmentCampaign Model (src/db/models/acknowledgment_campaign.py):**

```python
class AcknowledgmentCampaign(Base, UUIDMixin, TimestampMixin):
    """Mass acknowledgment campaign for a document."""

    # Document being acknowledged (frozen at campaign creation)
    document_id: Mapped[UUID]                  # FK to pages
    document_version: Mapped[str]              # Version at campaign creation
    git_commit_sha: Mapped[str]                # Frozen content version

    # Campaign metadata
    name: Mapped[str]                          # "Code of Conduct 2025 Acknowledgment"
    description: Mapped[str | None]
    created_by_id: Mapped[UUID]                # Admin who created

    # Timing
    start_date: Mapped[datetime]
    due_date: Mapped[datetime]

    # Assessment configuration (optional - default: disabled)
    requires_assessment: Mapped[bool] = False
    assessment_config_id: Mapped[UUID | None]  # FK to assessment config

    # Signature requirements
    requires_read_confirmation: Mapped[bool] = True
    minimum_read_time_seconds: Mapped[int | None] = None
    custom_attestation_text: Mapped[str | None] = None

    # Reminder configuration
    reminder_enabled: Mapped[bool] = True
    reminder_interval_hours: Mapped[int] = 24
    reminder_max_count: Mapped[int | None] = 3

    # Status
    status: Mapped[str]                        # "draft", "active", "completed", "cancelled"

    # Relationships
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="campaign")


class Assignment(Base, UUIDMixin, TimestampMixin):
    """Individual assignment for a user to acknowledge a document."""

    # Links
    campaign_id: Mapped[UUID]                  # FK to acknowledgment_campaigns
    user_id: Mapped[UUID]                      # FK to users

    # Progress tracking
    status: Mapped[str]                        # "pending", "in_progress", "completed", "overdue"
    document_read_at: Mapped[datetime | None]
    document_read_duration_seconds: Mapped[int | None]
    assessment_passed_at: Mapped[datetime | None]
    acknowledged_at: Mapped[datetime | None]

    # Signature link (created on acknowledgment)
    signature_id: Mapped[UUID | None]          # FK to electronic_signatures

    # Reminder tracking
    last_reminder_sent_at: Mapped[datetime | None]
    reminder_count: Mapped[int] = 0

    # Relationships
    campaign: Mapped["AcknowledgmentCampaign"] = relationship(back_populates="assignments")
    assessment_attempts: Mapped[list["AssessmentAttempt"]] = relationship()
    signature: Mapped["ElectronicSignature | None"] = relationship()


class AssessmentAttempt(Base, UUIDMixin, TimestampMixin):
    """Record of a user's assessment attempt."""

    assignment_id: Mapped[UUID]                # FK to assignments
    attempt_number: Mapped[int]

    # Questions and answers
    questions_presented: Mapped[list[dict]]    # [{question_id, source_ref}]
    answers: Mapped[dict]                      # {question_id: answer}

    # Results
    score: Mapped[int]                         # Correct answers
    total_questions: Mapped[int]
    passed: Mapped[bool]

    # Timing
    started_at: Mapped[datetime]
    completed_at: Mapped[datetime | None]
    time_taken_seconds: Mapped[int | None]
```

**Services Required:**

```python
# CampaignService (src/modules/acknowledgment/campaign_service.py)
class CampaignService:
    async def create_campaign(
        self,
        document_id: UUID,
        name: str,
        recipient_ids: list[UUID],
        due_date: datetime,
        requires_assessment: bool = False,
        assessment_config_id: UUID | None = None,
    ) -> AcknowledgmentCampaign:
        """Create campaign and assignments for all recipients."""

    async def get_campaign_status(
        self,
        campaign_id: UUID,
    ) -> CampaignStatusReport:
        """Get completion statistics for a campaign."""


# AssignmentService (src/modules/acknowledgment/assignment_service.py)
class AssignmentService:
    async def get_user_assignments(
        self,
        user_id: UUID,
        status: str | None = None,
    ) -> list[Assignment]:
        """Get assignments for a user (for dashboard)."""

    async def record_document_read(
        self,
        assignment_id: UUID,
        duration_seconds: int,
    ) -> Assignment:
        """Record that user has read the document."""

    async def complete_acknowledgment(
        self,
        assignment_id: UUID,
        user: User,
        password: str,  # Re-authentication
    ) -> ElectronicSignature:
        """
        Create signature for acknowledgment.
        - Verify assessment passed (if required)
        - Verify document read (if required)
        - Create ElectronicSignature with meaning=ACKNOWLEDGED
        - Link signature to assignment
        """
```

**API Endpoints:**
- `POST /api/v1/campaigns` - Create acknowledgment campaign
- `GET /api/v1/campaigns/{id}` - Get campaign details
- `GET /api/v1/campaigns/{id}/status` - Get completion statistics
- `GET /api/v1/assignments/me` - Get current user's assignments
- `POST /api/v1/assignments/{id}/read` - Record document read
- `POST /api/v1/assignments/{id}/acknowledge` - Complete acknowledgment (sign)
- `POST /api/v1/assignments/{id}/assessment/start` - Start assessment
- `POST /api/v1/assignments/{id}/assessment/submit` - Submit assessment answers

**Tests Required:**
- Unit: Campaign creation with assignments
- Unit: Assignment status transitions
- Unit: Assessment pass/fail logic
- Integration: Full acknowledgment flow (read → assess → sign)
- Integration: Campaign completion tracking
- Compliance: Signature creation for acknowledgment
- Compliance: Assessment attempt tracking

---

## Compliance Validation Checklist

### 21 CFR Part 11 - Electronic Records

| Requirement | Section | Sprint | Verification |
|-------------|---------|--------|--------------|
| Access control | §11.10(d) | 5 | Permission tests pass |
| Audit trail | §11.10(e) | 8 | Chain integrity test |
| Authority checks | §11.10(g) | 5 | Permission enforcement tests |
| Device checks | §11.10(c) | 1 | Git SHA integrity |

### 21 CFR Part 11 - Electronic Signatures

| Requirement | Section | Sprint | Verification |
|-------------|---------|--------|--------------|
| Manifestation | §11.50 | 7 | Signature display tests |
| Name + date/time | §11.50(a)(b) | 7 | Timestamp tests |
| Meaning | §11.50(a) | 7 | Meaning capture tests |
| Linking | §11.70 | 7 | Content hash tests |
| Uniqueness | §11.100(a) | 7 | User uniqueness tests |
| Re-authentication | §11.200 | 7 | Re-auth flow tests |

### ISO 9001/13485 - Document Control

| Requirement | ISO 9001 | ISO 13485 | Sprint | Verification |
|-------------|----------|-----------|--------|--------------|
| Approval before release | 7.5.2 | 4.2.4 | 6-7 | Workflow tests |
| Document identification | 7.5.3.1 | 4.2.4 | 6 | Numbering tests |
| Version control | 7.5.2 | 4.2.4 | 1, 6 | Git + revision tests |
| Change control | 7.5.2 | 4.2.5 | 6 | Change reason tests |
| Periodic review | 7.5.2 | 4.2.4 | 6 | Review reminder tests |
| Distribution control | 7.5.3.1 | 4.2.4 | 5 | Permission tests |
| Obsolete prevention | 7.5.3.2 | 4.2.4 | 6 | Supersession tests |

### IQ/OQ/PQ Requirements

Before production deployment, execute:
1. **IQ (Installation Qualification)** - Verify database schema, triggers, indexes
2. **OQ (Operational Qualification)** - Execute all compliance tests
3. **PQ (Performance Qualification)** - Load testing under expected conditions

---

## Required Documentation for Compliance

### System Documentation
- [ ] System Design Specification (SDS)
- [ ] User Requirements Specification (URS)
- [ ] Functional Requirements Specification (FRS)
- [ ] Risk Assessment (FMEA)
- [ ] Validation Plan (IQ/OQ/PQ protocols)

### SOPs Required
- [ ] SOP: Document Creation and Approval
- [ ] SOP: Electronic Signature Use
- [ ] SOP: Access Control Management
- [ ] SOP: Audit Trail Review
- [ ] SOP: System Administration and Backup
- [ ] SOP: Change Control for System Updates

### Training Requirements
- [ ] System administrator training
- [ ] Document author training
- [ ] Approver/reviewer training
- [ ] Audit trail review training
