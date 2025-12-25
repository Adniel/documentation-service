# Sprint 6: Document Control - Detailed Implementation Plan

## Overview

Sprint 6 implements ISO-compliant document control features for regulated document management.

**Compliance Scope:**
- ISO 9001:2015 §7.5.2 - Creating and updating documented information
- ISO 13485:2016 §4.2.4 - Control of documents
- ISO 13485:2016 §4.2.5 - Control of records
- ISO 15489 - Records management

**Design Decisions (Confirmed):**
- Lifecycle: Simple 5-state default, configurable per organization
- Numbering: Organization-level sequences per document type
- Approvals: Extend existing Change Request system
- Automation: Configurable per retention/review policy

---

## 1. Document Lifecycle State Machine

### Default States (5-State Model)

```
┌─────────┐     submit      ┌───────────┐    approve     ┌──────────┐
│  DRAFT  │ ───────────────►│ IN_REVIEW │ ──────────────►│ APPROVED │
└─────────┘                 └───────────┘                └──────────┘
     ▲                            │                            │
     │                            │ reject                     │ make effective
     │                            ▼                            ▼
     │                      ┌───────────┐              ┌───────────┐
     └──────────────────────│  (back to │              │ EFFECTIVE │
        revise              │   draft)  │              └───────────┘
                            └───────────┘                    │
                                                             │ obsolete
                                                             ▼
                                                       ┌──────────┐
                                                       │ OBSOLETE │
                                                       └──────────┘
```

### State Definitions

| State | Description | Editable | Visible to Viewers |
|-------|-------------|----------|-------------------|
| `DRAFT` | Work in progress, not submitted | Yes | No (author only) |
| `IN_REVIEW` | Submitted for approval | No | Reviewers only |
| `APPROVED` | Approved, awaiting effective date | No | Yes (with badge) |
| `EFFECTIVE` | Current active version | No | Yes |
| `OBSOLETE` | Superseded or retired | No | With warning |

### Allowed Transitions

```python
# src/db/models/document_lifecycle.py

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EFFECTIVE = "effective"
    OBSOLETE = "obsolete"

# Default transition rules
DEFAULT_TRANSITIONS: dict[DocumentStatus, list[DocumentStatus]] = {
    DocumentStatus.DRAFT: [DocumentStatus.IN_REVIEW],
    DocumentStatus.IN_REVIEW: [DocumentStatus.DRAFT, DocumentStatus.APPROVED],
    DocumentStatus.APPROVED: [DocumentStatus.EFFECTIVE, DocumentStatus.DRAFT],  # Can revert if issues found
    DocumentStatus.EFFECTIVE: [DocumentStatus.OBSOLETE],  # New revision creates new DRAFT
    DocumentStatus.OBSOLETE: [],  # Terminal state
}

# Who can trigger transitions
TRANSITION_PERMISSIONS: dict[tuple[DocumentStatus, DocumentStatus], Role] = {
    (DocumentStatus.DRAFT, DocumentStatus.IN_REVIEW): Role.EDITOR,      # Author submits
    (DocumentStatus.IN_REVIEW, DocumentStatus.DRAFT): Role.REVIEWER,    # Reviewer rejects
    (DocumentStatus.IN_REVIEW, DocumentStatus.APPROVED): Role.REVIEWER, # Reviewer approves
    (DocumentStatus.APPROVED, DocumentStatus.EFFECTIVE): Role.ADMIN,    # Admin activates
    (DocumentStatus.APPROVED, DocumentStatus.DRAFT): Role.ADMIN,        # Admin reverts
    (DocumentStatus.EFFECTIVE, DocumentStatus.OBSOLETE): Role.ADMIN,    # Admin obsoletes
}
```

### Configurable Lifecycle (Per Organization)

```python
# src/db/models/lifecycle_config.py

class LifecycleConfig(Base, UUIDMixin, TimestampMixin):
    """Organization-specific document lifecycle configuration."""

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), unique=True)

    # State configuration (JSON)
    states: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    # Example: [{"name": "draft", "label": "Draft", "editable": true, "visible": false}]

    # Transition rules (JSON)
    transitions: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    # Example: [{"from": "draft", "to": "in_review", "required_role": "editor"}]

    # Use defaults if not configured
    use_defaults: Mapped[bool] = mapped_column(default=True)
```

---

## 2. Document Numbering Service

### Database Schema

```python
# src/db/models/document_number.py

class DocumentNumberSequence(Base, UUIDMixin, TimestampMixin):
    """Auto-incrementing sequence for document numbers per org/type."""

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    document_type: Mapped[str] = mapped_column(String(50))  # SOP, WI, FORM, etc.

    # Sequence configuration
    prefix: Mapped[str] = mapped_column(String(50))  # e.g., "SOP-QMS"
    current_number: Mapped[int] = mapped_column(default=0)
    format_pattern: Mapped[str] = mapped_column(default="{prefix}-{number:03d}")

    # Constraints
    __table_args__ = (
        UniqueConstraint("organization_id", "document_type", name="uq_org_doctype_sequence"),
    )


class DocumentType(str, Enum):
    """Standard document types for regulated environments."""
    SOP = "sop"                    # Standard Operating Procedure
    WI = "wi"                      # Work Instruction
    FORM = "form"                  # Form/Template
    POLICY = "policy"              # Policy Document
    RECORD = "record"              # Record (filled form)
    SPECIFICATION = "specification" # Technical Specification
    MANUAL = "manual"              # Manual/Handbook
    GUIDELINE = "guideline"        # Guideline
    PROTOCOL = "protocol"          # Protocol (e.g., test protocol)


# Default prefixes per document type
DEFAULT_PREFIXES: dict[DocumentType, str] = {
    DocumentType.SOP: "SOP",
    DocumentType.WI: "WI",
    DocumentType.FORM: "FRM",
    DocumentType.POLICY: "POL",
    DocumentType.RECORD: "REC",
    DocumentType.SPECIFICATION: "SPEC",
    DocumentType.MANUAL: "MAN",
    DocumentType.GUIDELINE: "GL",
    DocumentType.PROTOCOL: "PROT",
}
```

### Service Implementation

```python
# src/modules/document_control/numbering_service.py

class DocumentNumberingService:
    """Service for generating unique document numbers."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_document_number(
        self,
        organization_id: UUID,
        document_type: DocumentType,
        custom_prefix: str | None = None,
    ) -> str:
        """
        Generate next document number for organization/type.

        Uses SELECT FOR UPDATE to prevent race conditions.

        Returns: Document number like "SOP-QMS-001"
        """
        # Get or create sequence with row lock
        result = await self.db.execute(
            select(DocumentNumberSequence)
            .where(
                DocumentNumberSequence.organization_id == organization_id,
                DocumentNumberSequence.document_type == document_type.value,
            )
            .with_for_update()
        )
        sequence = result.scalar_one_or_none()

        if not sequence:
            # Create new sequence
            prefix = custom_prefix or DEFAULT_PREFIXES.get(document_type, document_type.value.upper())
            sequence = DocumentNumberSequence(
                organization_id=organization_id,
                document_type=document_type.value,
                prefix=prefix,
                current_number=0,
            )
            self.db.add(sequence)

        # Increment and generate
        sequence.current_number += 1
        document_number = sequence.format_pattern.format(
            prefix=sequence.prefix,
            number=sequence.current_number,
        )

        await self.db.flush()
        return document_number

    async def validate_document_number(
        self,
        document_number: str,
        exclude_page_id: UUID | None = None,
    ) -> bool:
        """Check if document number is unique."""
        query = select(Page).where(Page.document_number == document_number)
        if exclude_page_id:
            query = query.where(Page.id != exclude_page_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is None

    async def configure_sequence(
        self,
        organization_id: UUID,
        document_type: DocumentType,
        prefix: str,
        format_pattern: str = "{prefix}-{number:03d}",
    ) -> DocumentNumberSequence:
        """Configure or update numbering for a document type."""
        result = await self.db.execute(
            select(DocumentNumberSequence)
            .where(
                DocumentNumberSequence.organization_id == organization_id,
                DocumentNumberSequence.document_type == document_type.value,
            )
        )
        sequence = result.scalar_one_or_none()

        if sequence:
            sequence.prefix = prefix
            sequence.format_pattern = format_pattern
        else:
            sequence = DocumentNumberSequence(
                organization_id=organization_id,
                document_type=document_type.value,
                prefix=prefix,
                format_pattern=format_pattern,
                current_number=0,
            )
            self.db.add(sequence)

        await self.db.flush()
        return sequence
```

---

## 3. Page Model Additions

### Schema Updates

```python
# src/db/models/page.py - Additions to existing Page model

class Page(Base, UUIDMixin, TimestampMixin):
    # ... existing fields ...

    # === DOCUMENT CONTROL FIELDS (Sprint 6) ===

    # Document Identification (ISO 13485 §4.2.4)
    document_type: Mapped[str | None] = mapped_column(String(50))
    document_number: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    is_controlled: Mapped[bool] = mapped_column(default=False)  # True = requires document control

    # Revision Tracking (ISO 13485 §4.2.5)
    revision: Mapped[str] = mapped_column(String(20), default="A")  # A, B, C...
    major_version: Mapped[int] = mapped_column(default=1)
    minor_version: Mapped[int] = mapped_column(default=0)

    # Lifecycle Status
    document_status: Mapped[str] = mapped_column(String(50), default="draft")

    # Date Tracking (ISO 9001 §7.5.2)
    approved_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    effective_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Review Scheduling
    review_cycle_months: Mapped[int | None]  # How often to review (e.g., 12 = annual)
    next_review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_reviewed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_reviewed_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))

    # Ownership (ISO 13485 §4.2.4)
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    custodian_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))

    # Retention (ISO 15489)
    retention_policy_id: Mapped[UUID | None] = mapped_column(ForeignKey("retention_policies.id"))
    disposition_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Supersession
    supersedes_id: Mapped[UUID | None] = mapped_column(ForeignKey("pages.id"))
    superseded_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("pages.id"))

    # Change Control (ISO 13485 §4.2.5)
    change_summary: Mapped[str | None] = mapped_column(Text)  # Brief description
    change_reason: Mapped[str | None] = mapped_column(Text)   # Why changed (required for major)

    # Training Requirement
    requires_training: Mapped[bool] = mapped_column(default=False)
    training_validity_months: Mapped[int | None]

    # Relationships
    owner: Mapped["User | None"] = relationship(foreign_keys=[owner_id])
    custodian: Mapped["User | None"] = relationship(foreign_keys=[custodian_id])
    approved_by: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])
    last_reviewed_by: Mapped["User | None"] = relationship(foreign_keys=[last_reviewed_by_id])
    supersedes: Mapped["Page | None"] = relationship(foreign_keys=[supersedes_id], remote_side="Page.id")
    superseded_by: Mapped["Page | None"] = relationship(foreign_keys=[superseded_by_id], remote_side="Page.id")
    retention_policy: Mapped["RetentionPolicy | None"] = relationship()
```

---

## 4. Retention Policy System

### Database Schema

```python
# src/db/models/retention_policy.py

class DispositionMethod(str, Enum):
    ARCHIVE = "archive"       # Move to archive storage
    DESTROY = "destroy"       # Permanently delete
    TRANSFER = "transfer"     # Transfer to external system
    REVIEW = "review"         # Requires manual review before disposition

class ExpirationAction(str, Enum):
    NOTIFY_ONLY = "notify_only"           # Send notification, no state change
    AUTO_STATE_CHANGE = "auto_state_change"  # Automatically change state
    BLOCK_ACCESS = "block_access"          # Block access until reviewed


class RetentionPolicy(Base, UUIDMixin, TimestampMixin):
    """Configurable retention policy for documents."""

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))

    # Policy identification
    name: Mapped[str] = mapped_column(String(100))  # e.g., "QMS Records - 7 Years"
    description: Mapped[str | None] = mapped_column(Text)

    # Applicable document types (empty = all types)
    applicable_document_types: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # Retention period
    retention_years: Mapped[int]  # How long to keep after effective date
    retention_from: Mapped[str] = mapped_column(default="effective_date")
    # Options: "effective_date", "obsolete_date", "created_date"

    # Disposition
    disposition_method: Mapped[DispositionMethod]

    # Review due behavior
    review_overdue_action: Mapped[ExpirationAction] = mapped_column(
        default=ExpirationAction.NOTIFY_ONLY
    )
    review_overdue_grace_days: Mapped[int] = mapped_column(default=30)

    # Retention expiration behavior
    retention_expiry_action: Mapped[ExpirationAction] = mapped_column(
        default=ExpirationAction.NOTIFY_ONLY
    )
    retention_expiry_grace_days: Mapped[int] = mapped_column(default=90)

    # Notification settings
    notify_owner: Mapped[bool] = mapped_column(default=True)
    notify_custodian: Mapped[bool] = mapped_column(default=True)
    notify_days_before: Mapped[list[int]] = mapped_column(JSONB, default=lambda: [30, 7, 1])

    # Active flag
    is_active: Mapped[bool] = mapped_column(default=True)
```

### Service Implementation

```python
# src/modules/document_control/retention_service.py

class RetentionService:
    """Service for managing document retention and disposition."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_retention_policy(
        self,
        page: Page,
        policy: RetentionPolicy,
    ) -> Page:
        """Apply retention policy to a document."""
        page.retention_policy_id = policy.id

        # Calculate disposition date based on policy
        if policy.retention_from == "effective_date" and page.effective_date:
            base_date = page.effective_date
        elif policy.retention_from == "obsolete_date" and page.document_status == "obsolete":
            base_date = page.updated_at  # When it became obsolete
        else:
            base_date = page.created_at

        page.disposition_date = base_date + timedelta(days=policy.retention_years * 365)

        await self.db.flush()
        return page

    async def get_documents_due_for_review(
        self,
        organization_id: UUID,
        include_overdue: bool = True,
        days_ahead: int = 30,
    ) -> list[Page]:
        """Get documents due for periodic review."""
        now = datetime.now(timezone.utc)
        future_date = now + timedelta(days=days_ahead)

        conditions = [
            Page.is_controlled == True,
            Page.document_status == DocumentStatus.EFFECTIVE.value,
            Page.next_review_date.isnot(None),
        ]

        if include_overdue:
            conditions.append(Page.next_review_date <= future_date)
        else:
            conditions.append(
                and_(
                    Page.next_review_date > now,
                    Page.next_review_date <= future_date,
                )
            )

        # Filter by org through space hierarchy
        result = await self.db.execute(
            select(Page)
            .join(Space, Page.space_id == Space.id)
            .join(Workspace, Space.workspace_id == Workspace.id)
            .where(
                Workspace.organization_id == organization_id,
                and_(*conditions),
            )
            .order_by(Page.next_review_date)
        )
        return list(result.scalars().all())

    async def get_documents_due_for_disposition(
        self,
        organization_id: UUID,
        days_ahead: int = 90,
    ) -> list[Page]:
        """Get documents approaching or past disposition date."""
        future_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)

        result = await self.db.execute(
            select(Page)
            .join(Space, Page.space_id == Space.id)
            .join(Workspace, Space.workspace_id == Workspace.id)
            .where(
                Workspace.organization_id == organization_id,
                Page.disposition_date.isnot(None),
                Page.disposition_date <= future_date,
                Page.document_status != DocumentStatus.OBSOLETE.value,
            )
            .order_by(Page.disposition_date)
        )
        return list(result.scalars().all())

    async def execute_disposition(
        self,
        page: Page,
        executed_by_id: UUID,
        reason: str,
    ) -> Page:
        """Execute disposition action on a document."""
        policy = page.retention_policy

        if policy.disposition_method == DispositionMethod.ARCHIVE:
            # Mark as archived (keep but restrict access)
            page.document_status = DocumentStatus.OBSOLETE.value
            page.change_reason = f"Archived per retention policy: {reason}"

        elif policy.disposition_method == DispositionMethod.DESTROY:
            # Soft delete (actual deletion requires separate process)
            page.is_deleted = True
            page.deleted_at = datetime.now(timezone.utc)
            page.change_reason = f"Destroyed per retention policy: {reason}"

        elif policy.disposition_method == DispositionMethod.TRANSFER:
            # Mark for transfer (external process handles actual transfer)
            page.document_status = DocumentStatus.OBSOLETE.value
            page.change_reason = f"Transferred per retention policy: {reason}"

        # Log to audit trail
        # (audit service call here)

        await self.db.flush()
        return page
```

---

## 5. Change Request Integration (Approval Workflow)

### Extended Change Request Model

```python
# src/db/models/change_request.py - Additions

class ChangeRequest(Base, UUIDMixin, TimestampMixin):
    # ... existing fields from Sprint 4 ...

    # === APPROVAL WORKFLOW FIELDS (Sprint 6) ===

    # Approval matrix reference
    approval_matrix_id: Mapped[UUID | None] = mapped_column(ForeignKey("approval_matrices.id"))

    # Current approval step
    current_approval_step: Mapped[int] = mapped_column(default=0)

    # Approval status
    approval_status: Mapped[str] = mapped_column(default="pending")
    # Values: "pending", "in_progress", "approved", "rejected"

    # Document control metadata (for controlled documents)
    is_major_revision: Mapped[bool] = mapped_column(default=False)
    change_reason: Mapped[str | None] = mapped_column(Text)  # Required for major revisions

    # Relationships
    approval_matrix: Mapped["ApprovalMatrix | None"] = relationship()
    approval_records: Mapped[list["ApprovalRecord"]] = relationship(back_populates="change_request")


class ApprovalMatrix(Base, UUIDMixin, TimestampMixin):
    """Defines approval requirements for document types."""

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(100))  # e.g., "SOP Approval - 2 Levels"
    description: Mapped[str | None] = mapped_column(Text)

    # Applicable document types (empty = all)
    applicable_document_types: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # Approval steps (ordered)
    steps: Mapped[list[dict]] = mapped_column(JSONB)
    # Example:
    # [
    #   {"order": 1, "name": "Technical Review", "role": "reviewer", "required": true},
    #   {"order": 2, "name": "QA Approval", "role": "qa_approver", "required": true},
    #   {"order": 3, "name": "Management Approval", "role": "admin", "required": false}
    # ]

    # All required steps must complete, optional steps can be skipped
    require_sequential: Mapped[bool] = mapped_column(default=True)

    is_active: Mapped[bool] = mapped_column(default=True)


class ApprovalRecord(Base, UUIDMixin, TimestampMixin):
    """Individual approval action within a change request."""

    change_request_id: Mapped[UUID] = mapped_column(ForeignKey("change_requests.id"))

    # Approval step info
    step_order: Mapped[int]
    step_name: Mapped[str] = mapped_column(String(100))

    # Approver
    approver_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Decision
    decision: Mapped[str] = mapped_column(String(50))  # "approved", "rejected", "skipped"
    comment: Mapped[str | None] = mapped_column(Text)

    # Timestamp
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    change_request: Mapped["ChangeRequest"] = relationship(back_populates="approval_records")
    approver: Mapped["User"] = relationship()
```

### Approval Service

```python
# src/modules/document_control/approval_service.py

class ApprovalService:
    """Service for managing document approval workflows."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initiate_approval(
        self,
        change_request: ChangeRequest,
        initiated_by_id: UUID,
    ) -> ChangeRequest:
        """
        Start approval workflow for a change request.

        Steps:
        1. Determine applicable approval matrix
        2. Set initial approval step
        3. Notify first approver(s)
        """
        page = change_request.page

        # Find applicable approval matrix
        matrix = await self._get_applicable_matrix(
            organization_id=page.space.workspace.organization_id,
            document_type=page.document_type,
        )

        if matrix:
            change_request.approval_matrix_id = matrix.id
            change_request.current_approval_step = 1
            change_request.approval_status = "in_progress"
        else:
            # No matrix = auto-approve (single approver workflow)
            change_request.approval_status = "pending"

        change_request.status = ChangeRequestStatus.IN_REVIEW
        await self.db.flush()

        # Notify approvers
        await self._notify_current_approvers(change_request)

        return change_request

    async def record_approval(
        self,
        change_request_id: UUID,
        approver_id: UUID,
        decision: str,  # "approved" | "rejected"
        comment: str | None = None,
    ) -> tuple[ChangeRequest, bool]:
        """
        Record an approval decision.

        Returns: (change_request, is_workflow_complete)
        """
        cr = await self.db.get(ChangeRequest, change_request_id)
        matrix = cr.approval_matrix

        if not matrix:
            # Simple approval (no matrix)
            cr.approval_status = decision
            cr.status = (
                ChangeRequestStatus.APPROVED if decision == "approved"
                else ChangeRequestStatus.CHANGES_REQUESTED
            )
            await self.db.flush()
            return cr, True

        # Record this approval
        current_step = matrix.steps[cr.current_approval_step - 1]

        record = ApprovalRecord(
            change_request_id=cr.id,
            step_order=cr.current_approval_step,
            step_name=current_step["name"],
            approver_id=approver_id,
            decision=decision,
            comment=comment,
            decided_at=datetime.now(timezone.utc),
        )
        self.db.add(record)

        if decision == "rejected":
            cr.approval_status = "rejected"
            cr.status = ChangeRequestStatus.CHANGES_REQUESTED
            await self.db.flush()
            return cr, True

        # Move to next step
        if cr.current_approval_step < len(matrix.steps):
            next_step = matrix.steps[cr.current_approval_step]
            if next_step.get("required", True):
                cr.current_approval_step += 1
                await self._notify_current_approvers(cr)
                await self.db.flush()
                return cr, False
            else:
                # Skip optional step
                cr.current_approval_step += 1

        # All steps complete
        cr.approval_status = "approved"
        cr.status = ChangeRequestStatus.APPROVED
        await self.db.flush()
        return cr, True

    async def _get_applicable_matrix(
        self,
        organization_id: UUID,
        document_type: str | None,
    ) -> ApprovalMatrix | None:
        """Find the approval matrix applicable to this document type."""
        result = await self.db.execute(
            select(ApprovalMatrix)
            .where(
                ApprovalMatrix.organization_id == organization_id,
                ApprovalMatrix.is_active == True,
            )
        )
        matrices = result.scalars().all()

        for matrix in matrices:
            if not matrix.applicable_document_types:
                return matrix  # Applies to all types
            if document_type in matrix.applicable_document_types:
                return matrix

        return None

    async def _notify_current_approvers(self, cr: ChangeRequest) -> None:
        """Send notifications to current step approvers."""
        # Implementation: email/notification service
        pass
```

---

## 6. Revision Service

```python
# src/modules/document_control/revision_service.py

class RevisionService:
    """Service for managing document revisions."""

    REVISION_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_new_revision(
        self,
        page: Page,
        is_major: bool,
        change_reason: str,
        author_id: UUID,
    ) -> ChangeRequest:
        """
        Create a new revision of an effective document.

        For controlled documents:
        - Major revision: Increment revision letter (A→B), reset version to 1.0
        - Minor revision: Increment minor version (1.0→1.1)

        Creates a new Change Request (draft branch) with the revision metadata.
        """
        if page.document_status != DocumentStatus.EFFECTIVE.value:
            raise ValueError("Can only create revisions of effective documents")

        # Calculate new revision/version
        if is_major:
            new_revision = self._next_revision_letter(page.revision)
            new_major = 1
            new_minor = 0
        else:
            new_revision = page.revision
            new_major = page.major_version
            new_minor = page.minor_version + 1

        # Create change request for revision
        from src.modules.content.change_request_service import ChangeRequestService
        cr_service = ChangeRequestService(self.db)

        change_request = await cr_service.create_draft(
            page_id=page.id,
            author_id=author_id,
            title=f"Revision {new_revision} v{new_major}.{new_minor}",
            description=change_reason,
        )

        # Store revision metadata on CR
        change_request.is_major_revision = is_major
        change_request.change_reason = change_reason

        # Store pending revision info (applied on publish)
        change_request.metadata = {
            "pending_revision": new_revision,
            "pending_major_version": new_major,
            "pending_minor_version": new_minor,
        }

        await self.db.flush()
        return change_request

    async def apply_revision(
        self,
        change_request: ChangeRequest,
        published_by_id: UUID,
    ) -> Page:
        """
        Apply revision metadata when publishing a change request.

        Called by ChangeRequestService.publish() for controlled documents.
        """
        page = change_request.page
        metadata = change_request.metadata or {}

        if "pending_revision" in metadata:
            # Store old version info for supersession tracking
            old_revision = f"{page.revision} v{page.major_version}.{page.minor_version}"

            # Apply new revision
            page.revision = metadata["pending_revision"]
            page.major_version = metadata["pending_major_version"]
            page.minor_version = metadata["pending_minor_version"]

            # Update change control fields
            page.change_summary = change_request.title
            page.change_reason = change_request.change_reason

        await self.db.flush()
        return page

    def _next_revision_letter(self, current: str) -> str:
        """Get next revision letter (A→B, Z→AA)."""
        if not current:
            return "A"

        if current in self.REVISION_LETTERS:
            idx = self.REVISION_LETTERS.index(current)
            if idx < len(self.REVISION_LETTERS) - 1:
                return self.REVISION_LETTERS[idx + 1]
            return "AA"  # After Z comes AA

        # Handle multi-letter (AA, AB, etc.)
        # Simplified: just increment last letter
        return current[:-1] + self._next_revision_letter(current[-1])

    async def get_revision_history(
        self,
        page_id: UUID,
    ) -> list[dict]:
        """Get complete revision history for a document."""
        # Get all published change requests for this page
        result = await self.db.execute(
            select(ChangeRequest)
            .where(
                ChangeRequest.page_id == page_id,
                ChangeRequest.status == ChangeRequestStatus.PUBLISHED,
            )
            .order_by(ChangeRequest.published_at.desc())
        )

        history = []
        for cr in result.scalars():
            history.append({
                "revision": cr.metadata.get("pending_revision") if cr.metadata else None,
                "version": f"{cr.metadata.get('pending_major_version', 1)}.{cr.metadata.get('pending_minor_version', 0)}" if cr.metadata else "1.0",
                "title": cr.title,
                "change_reason": cr.change_reason,
                "author_id": str(cr.author_id),
                "author_name": cr.author.full_name if cr.author else None,
                "published_at": cr.published_at.isoformat() if cr.published_at else None,
                "is_major": cr.is_major_revision,
            })

        return history
```

---

## 7. Document Metadata Service

```python
# src/modules/document_control/metadata_service.py

class DocumentMetadataService:
    """Service for validating and managing document metadata."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_for_transition(
        self,
        page: Page,
        from_status: DocumentStatus,
        to_status: DocumentStatus,
    ) -> list[str]:
        """
        Validate document has required metadata for status transition.

        Returns list of validation errors (empty = valid).
        """
        errors = []

        if not page.is_controlled:
            return errors  # Non-controlled documents skip validation

        # DRAFT → IN_REVIEW
        if to_status == DocumentStatus.IN_REVIEW:
            if not page.document_number:
                errors.append("Document number is required before review")
            if not page.owner_id:
                errors.append("Document owner must be assigned")

        # IN_REVIEW → APPROVED
        if to_status == DocumentStatus.APPROVED:
            if not page.document_type:
                errors.append("Document type must be specified")

        # APPROVED → EFFECTIVE
        if to_status == DocumentStatus.EFFECTIVE:
            if not page.effective_date:
                errors.append("Effective date must be set")
            if page.effective_date and page.effective_date < page.approved_date:
                errors.append("Effective date cannot be before approved date")
            if page.review_cycle_months and not page.next_review_date:
                errors.append("Next review date must be set for periodic review")

            # Check retention policy for required document types
            if page.document_type in ["record", "form"] and not page.retention_policy_id:
                errors.append(f"Retention policy required for {page.document_type} documents")

        # Major revision requires change reason
        if hasattr(page, '_pending_major_revision') and page._pending_major_revision:
            if not page.change_reason:
                errors.append("Change reason required for major revisions")

        return errors

    async def set_effective(
        self,
        page: Page,
        effective_date: datetime,
        set_by_id: UUID,
    ) -> Page:
        """Make a document effective and calculate next review date."""
        page.effective_date = effective_date
        page.document_status = DocumentStatus.EFFECTIVE.value

        # Calculate next review date if review cycle is set
        if page.review_cycle_months:
            page.next_review_date = effective_date + timedelta(days=page.review_cycle_months * 30)

        await self.db.flush()
        return page

    async def complete_review(
        self,
        page: Page,
        reviewed_by_id: UUID,
        next_review_months: int | None = None,
    ) -> Page:
        """Record periodic review completion."""
        now = datetime.now(timezone.utc)

        page.last_reviewed_date = now
        page.last_reviewed_by_id = reviewed_by_id

        # Calculate next review date
        review_cycle = next_review_months or page.review_cycle_months
        if review_cycle:
            page.next_review_date = now + timedelta(days=review_cycle * 30)

        await self.db.flush()
        return page

    async def mark_obsolete(
        self,
        page: Page,
        superseded_by_id: UUID | None,
        reason: str,
        marked_by_id: UUID,
    ) -> Page:
        """Mark document as obsolete."""
        page.document_status = DocumentStatus.OBSOLETE.value
        page.change_reason = reason

        if superseded_by_id:
            page.superseded_by_id = superseded_by_id
            # Also update the new document to reference what it supersedes
            new_doc = await self.db.get(Page, superseded_by_id)
            if new_doc:
                new_doc.supersedes_id = page.id

        await self.db.flush()
        return page
```

---

## 8. API Endpoints

### Document Control Routes

```python
# src/api/endpoints/document_control.py

router = APIRouter(prefix="/document-control", tags=["Document Control"])


@router.post("/documents/{page_id}/number", response_model=DocumentNumberResponse)
async def generate_document_number(
    page_id: UUID,
    document_type: DocumentType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentNumberResponse:
    """Generate unique document number for a page."""
    page = await get_page_or_404(db, page_id)
    check_permission(current_user, page, Role.EDITOR)

    # Get organization from page hierarchy
    org_id = await get_page_organization_id(db, page)

    numbering_service = DocumentNumberingService(db)
    document_number = await numbering_service.generate_document_number(
        organization_id=org_id,
        document_type=document_type,
    )

    # Assign to page
    page.document_number = document_number
    page.document_type = document_type.value
    page.is_controlled = True

    # Log to audit trail
    await audit_service.log_event(...)

    await db.commit()
    return DocumentNumberResponse(document_number=document_number)


@router.post("/documents/{page_id}/revise", response_model=ChangeRequestResponse)
async def create_revision(
    page_id: UUID,
    data: CreateRevisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChangeRequestResponse:
    """Create a new revision of an effective document."""
    page = await get_page_or_404(db, page_id)
    check_permission(current_user, page, Role.EDITOR)

    revision_service = RevisionService(db)
    change_request = await revision_service.create_new_revision(
        page=page,
        is_major=data.is_major,
        change_reason=data.change_reason,
        author_id=current_user.id,
    )

    await db.commit()
    return ChangeRequestResponse.from_model(change_request)


@router.get("/documents/{page_id}/revisions", response_model=RevisionHistoryResponse)
async def get_revision_history(
    page_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RevisionHistoryResponse:
    """Get complete revision history for a document."""
    page = await get_page_or_404(db, page_id)
    check_permission(current_user, page, Role.VIEWER)

    revision_service = RevisionService(db)
    history = await revision_service.get_revision_history(page_id)

    return RevisionHistoryResponse(revisions=history)


@router.post("/documents/{page_id}/status", response_model=DocumentStatusResponse)
async def transition_status(
    page_id: UUID,
    data: StatusTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentStatusResponse:
    """Transition document to new lifecycle status."""
    page = await get_page_or_404(db, page_id)

    # Check transition permission
    lifecycle_service = LifecycleService(db)
    can_transition = await lifecycle_service.check_transition_permission(
        page=page,
        user=current_user,
        from_status=DocumentStatus(page.document_status),
        to_status=data.to_status,
    )
    if not can_transition:
        raise HTTPException(status_code=403, detail="Not authorized for this transition")

    # Validate metadata
    metadata_service = DocumentMetadataService(db)
    errors = await metadata_service.validate_for_transition(
        page=page,
        from_status=DocumentStatus(page.document_status),
        to_status=data.to_status,
    )
    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})

    # Execute transition
    page.document_status = data.to_status.value

    # Handle specific transitions
    if data.to_status == DocumentStatus.EFFECTIVE:
        await metadata_service.set_effective(
            page=page,
            effective_date=data.effective_date or datetime.now(timezone.utc),
            set_by_id=current_user.id,
        )
    elif data.to_status == DocumentStatus.OBSOLETE:
        await metadata_service.mark_obsolete(
            page=page,
            superseded_by_id=data.superseded_by_id,
            reason=data.reason,
            marked_by_id=current_user.id,
        )

    # Log to audit trail
    await audit_service.log_event(...)

    await db.commit()
    return DocumentStatusResponse.from_model(page)


@router.get("/review-due", response_model=DocumentListResponse)
async def get_documents_due_for_review(
    days_ahead: int = Query(30, ge=1, le=365),
    include_overdue: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """Get documents due for periodic review."""
    org_id = current_user.organization_id  # Or from query param

    retention_service = RetentionService(db)
    documents = await retention_service.get_documents_due_for_review(
        organization_id=org_id,
        include_overdue=include_overdue,
        days_ahead=days_ahead,
    )

    return DocumentListResponse(items=[...])


@router.get("/retention-due", response_model=DocumentListResponse)
async def get_documents_due_for_disposition(
    days_ahead: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """Get documents approaching disposition date."""
    org_id = current_user.organization_id

    retention_service = RetentionService(db)
    documents = await retention_service.get_documents_due_for_disposition(
        organization_id=org_id,
        days_ahead=days_ahead,
    )

    return DocumentListResponse(items=[...])
```

### Approval Workflow Routes

```python
# src/api/endpoints/approvals.py

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/change-requests/{cr_id}/approve", response_model=ApprovalResponse)
async def approve_change_request(
    cr_id: UUID,
    data: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """Record approval decision for a change request."""
    cr = await get_change_request_or_404(db, cr_id)

    # Verify user is authorized to approve current step
    await verify_approver(current_user, cr)

    approval_service = ApprovalService(db)
    cr, is_complete = await approval_service.record_approval(
        change_request_id=cr_id,
        approver_id=current_user.id,
        decision=data.decision,
        comment=data.comment,
    )

    # Log to audit trail
    await audit_service.log_event(...)

    await db.commit()

    return ApprovalResponse(
        change_request_id=str(cr.id),
        approval_status=cr.approval_status,
        is_workflow_complete=is_complete,
        current_step=cr.current_approval_step,
    )


@router.get("/matrices", response_model=ApprovalMatrixListResponse)
async def list_approval_matrices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApprovalMatrixListResponse:
    """List approval matrices for the organization."""
    # Implementation
    pass


@router.post("/matrices", response_model=ApprovalMatrixResponse)
async def create_approval_matrix(
    data: ApprovalMatrixCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ApprovalMatrixResponse:
    """Create a new approval matrix."""
    # Implementation
    pass
```

---

## 9. Frontend Components

### Document Control Panel

```typescript
// frontend/src/components/document-control/DocumentControlPanel.tsx

interface DocumentControlPanelProps {
  page: Page;
  onUpdate: () => void;
}

export function DocumentControlPanel({ page, onUpdate }: DocumentControlPanelProps) {
  return (
    <div className="document-control-panel">
      {/* Document Identification */}
      <section>
        <h3>Document Identification</h3>
        <dl>
          <dt>Document Number</dt>
          <dd>{page.documentNumber || <GenerateNumberButton pageId={page.id} />}</dd>

          <dt>Document Type</dt>
          <dd><DocumentTypeSelector value={page.documentType} /></dd>

          <dt>Revision</dt>
          <dd>{page.revision} v{page.majorVersion}.{page.minorVersion}</dd>
        </dl>
      </section>

      {/* Lifecycle Status */}
      <section>
        <h3>Status</h3>
        <DocumentStatusBadge status={page.documentStatus} />
        <StatusTransitionActions page={page} onTransition={onUpdate} />
      </section>

      {/* Dates */}
      <section>
        <h3>Dates</h3>
        <dl>
          <dt>Approved</dt>
          <dd>{formatDate(page.approvedDate)}</dd>

          <dt>Effective</dt>
          <dd>{formatDate(page.effectiveDate)}</dd>

          <dt>Next Review</dt>
          <dd>
            {formatDate(page.nextReviewDate)}
            {isOverdue(page.nextReviewDate) && <Badge variant="warning">Overdue</Badge>}
          </dd>
        </dl>
      </section>

      {/* Ownership */}
      <section>
        <h3>Ownership</h3>
        <OwnerSelector pageId={page.id} currentOwner={page.owner} />
        <CustodianSelector pageId={page.id} currentCustodian={page.custodian} />
      </section>

      {/* Retention */}
      {page.retentionPolicy && (
        <section>
          <h3>Retention</h3>
          <p>{page.retentionPolicy.name}</p>
          <p>Disposition: {formatDate(page.dispositionDate)}</p>
        </section>
      )}
    </div>
  );
}
```

### Approval Workflow Component

```typescript
// frontend/src/components/document-control/ApprovalWorkflow.tsx

interface ApprovalWorkflowProps {
  changeRequest: ChangeRequest;
  onApprove: () => void;
}

export function ApprovalWorkflow({ changeRequest, onApprove }: ApprovalWorkflowProps) {
  const { matrix, currentStep, approvalRecords } = changeRequest;

  return (
    <div className="approval-workflow">
      <h3>Approval Workflow</h3>

      {/* Progress indicator */}
      <div className="workflow-steps">
        {matrix?.steps.map((step, index) => (
          <WorkflowStep
            key={step.order}
            step={step}
            status={getStepStatus(index, currentStep, approvalRecords)}
            record={approvalRecords.find(r => r.stepOrder === step.order)}
          />
        ))}
      </div>

      {/* Action buttons for current approver */}
      {canApprove(currentUser, changeRequest) && (
        <div className="approval-actions">
          <ApproveButton crId={changeRequest.id} onSuccess={onApprove} />
          <RejectButton crId={changeRequest.id} onSuccess={onApprove} />
        </div>
      )}

      {/* Approval history */}
      <ApprovalHistory records={approvalRecords} />
    </div>
  );
}
```

### Review Dashboard

```typescript
// frontend/src/components/document-control/ReviewDashboard.tsx

export function ReviewDashboard() {
  const { data: reviewDue } = useQuery(['review-due'], fetchReviewDue);
  const { data: retentionDue } = useQuery(['retention-due'], fetchRetentionDue);

  return (
    <div className="review-dashboard">
      {/* Documents needing review */}
      <section>
        <h2>Periodic Review Due</h2>
        <DocumentTable
          documents={reviewDue}
          columns={['documentNumber', 'title', 'nextReviewDate', 'owner']}
          actions={['startReview']}
        />
      </section>

      {/* Documents approaching disposition */}
      <section>
        <h2>Retention Expiring</h2>
        <DocumentTable
          documents={retentionDue}
          columns={['documentNumber', 'title', 'dispositionDate', 'retentionPolicy']}
          actions={['executeDisposition', 'extendRetention']}
        />
      </section>
    </div>
  );
}
```

---

## 10. Database Migrations

### Migration 1: Document Control Fields on Page

```python
# alembic/versions/xxxx_add_document_control_fields.py

def upgrade():
    # Add document control columns to pages table
    op.add_column('pages', sa.Column('document_type', sa.String(50)))
    op.add_column('pages', sa.Column('document_number', sa.String(100)))
    op.add_column('pages', sa.Column('is_controlled', sa.Boolean(), default=False))
    op.add_column('pages', sa.Column('revision', sa.String(20), default='A'))
    op.add_column('pages', sa.Column('major_version', sa.Integer(), default=1))
    op.add_column('pages', sa.Column('minor_version', sa.Integer(), default=0))
    op.add_column('pages', sa.Column('document_status', sa.String(50), default='draft'))

    # Date tracking
    op.add_column('pages', sa.Column('approved_date', sa.DateTime(timezone=True)))
    op.add_column('pages', sa.Column('approved_by_id', sa.UUID()))
    op.add_column('pages', sa.Column('effective_date', sa.DateTime(timezone=True)))
    op.add_column('pages', sa.Column('review_cycle_months', sa.Integer()))
    op.add_column('pages', sa.Column('next_review_date', sa.DateTime(timezone=True)))
    op.add_column('pages', sa.Column('last_reviewed_date', sa.DateTime(timezone=True)))
    op.add_column('pages', sa.Column('last_reviewed_by_id', sa.UUID()))

    # Ownership
    op.add_column('pages', sa.Column('owner_id', sa.UUID()))
    op.add_column('pages', sa.Column('custodian_id', sa.UUID()))

    # Retention
    op.add_column('pages', sa.Column('retention_policy_id', sa.UUID()))
    op.add_column('pages', sa.Column('disposition_date', sa.DateTime(timezone=True)))

    # Supersession
    op.add_column('pages', sa.Column('supersedes_id', sa.UUID()))
    op.add_column('pages', sa.Column('superseded_by_id', sa.UUID()))

    # Change control
    op.add_column('pages', sa.Column('change_summary', sa.Text()))
    op.add_column('pages', sa.Column('change_reason', sa.Text()))

    # Training
    op.add_column('pages', sa.Column('requires_training', sa.Boolean(), default=False))
    op.add_column('pages', sa.Column('training_validity_months', sa.Integer()))

    # Indexes
    op.create_index('ix_pages_document_number', 'pages', ['document_number'], unique=True)
    op.create_index('ix_pages_document_status', 'pages', ['document_status'])
    op.create_index('ix_pages_next_review_date', 'pages', ['next_review_date'])

    # Foreign keys
    op.create_foreign_key('fk_pages_owner', 'pages', 'users', ['owner_id'], ['id'])
    op.create_foreign_key('fk_pages_custodian', 'pages', 'users', ['custodian_id'], ['id'])
    op.create_foreign_key('fk_pages_approved_by', 'pages', 'users', ['approved_by_id'], ['id'])
    op.create_foreign_key('fk_pages_reviewed_by', 'pages', 'users', ['last_reviewed_by_id'], ['id'])
    op.create_foreign_key('fk_pages_supersedes', 'pages', 'pages', ['supersedes_id'], ['id'])
    op.create_foreign_key('fk_pages_superseded_by', 'pages', 'pages', ['superseded_by_id'], ['id'])
```

### Migration 2: Document Numbering Sequences

```python
# alembic/versions/xxxx_create_document_number_sequences.py

def upgrade():
    op.create_table(
        'document_number_sequences',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('organization_id', sa.UUID(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('prefix', sa.String(50), nullable=False),
        sa.Column('current_number', sa.Integer(), nullable=False, default=0),
        sa.Column('format_pattern', sa.String(100), nullable=False, default='{prefix}-{number:03d}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('organization_id', 'document_type', name='uq_org_doctype_sequence'),
    )
```

### Migration 3: Retention Policies

```python
# alembic/versions/xxxx_create_retention_policies.py

def upgrade():
    op.create_table(
        'retention_policies',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('organization_id', sa.UUID(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('applicable_document_types', sa.JSON(), default=[]),
        sa.Column('retention_years', sa.Integer(), nullable=False),
        sa.Column('retention_from', sa.String(50), default='effective_date'),
        sa.Column('disposition_method', sa.String(50), nullable=False),
        sa.Column('review_overdue_action', sa.String(50), default='notify_only'),
        sa.Column('review_overdue_grace_days', sa.Integer(), default=30),
        sa.Column('retention_expiry_action', sa.String(50), default='notify_only'),
        sa.Column('retention_expiry_grace_days', sa.Integer(), default=90),
        sa.Column('notify_owner', sa.Boolean(), default=True),
        sa.Column('notify_custodian', sa.Boolean(), default=True),
        sa.Column('notify_days_before', sa.JSON(), default=[30, 7, 1]),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Add FK to pages
    op.create_foreign_key(
        'fk_pages_retention_policy',
        'pages', 'retention_policies',
        ['retention_policy_id'], ['id']
    )
```

### Migration 4: Approval Workflow Tables

```python
# alembic/versions/xxxx_create_approval_workflow_tables.py

def upgrade():
    # Approval matrices
    op.create_table(
        'approval_matrices',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('organization_id', sa.UUID(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('applicable_document_types', sa.JSON(), default=[]),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('require_sequential', sa.Boolean(), default=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Add approval fields to change_requests
    op.add_column('change_requests', sa.Column('approval_matrix_id', sa.UUID()))
    op.add_column('change_requests', sa.Column('current_approval_step', sa.Integer(), default=0))
    op.add_column('change_requests', sa.Column('approval_status', sa.String(50), default='pending'))
    op.add_column('change_requests', sa.Column('is_major_revision', sa.Boolean(), default=False))
    op.add_column('change_requests', sa.Column('change_reason', sa.Text()))
    op.add_column('change_requests', sa.Column('metadata', sa.JSON()))

    op.create_foreign_key(
        'fk_change_requests_approval_matrix',
        'change_requests', 'approval_matrices',
        ['approval_matrix_id'], ['id']
    )

    # Approval records
    op.create_table(
        'approval_records',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('change_request_id', sa.UUID(), sa.ForeignKey('change_requests.id'), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(100), nullable=False),
        sa.Column('approver_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('decision', sa.String(50), nullable=False),
        sa.Column('comment', sa.Text()),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
```

---

## 11. Test Plan

### Unit Tests

```python
# tests/unit/test_document_numbering.py
class TestDocumentNumberingService:
    async def test_generate_first_number(self): ...
    async def test_generate_sequential_numbers(self): ...
    async def test_concurrent_number_generation(self): ...  # Race condition test
    async def test_custom_prefix(self): ...
    async def test_format_pattern(self): ...

# tests/unit/test_revision_service.py
class TestRevisionService:
    async def test_major_revision_increments_letter(self): ...
    async def test_minor_revision_increments_version(self): ...
    async def test_revision_after_z(self): ...  # Z → AA
    async def test_revision_history(self): ...

# tests/unit/test_lifecycle_transitions.py
class TestLifecycleTransitions:
    async def test_valid_transitions(self): ...
    async def test_invalid_transitions(self): ...
    async def test_transition_permissions(self): ...
    async def test_metadata_validation_on_transition(self): ...

# tests/unit/test_retention_service.py
class TestRetentionService:
    async def test_apply_retention_policy(self): ...
    async def test_calculate_disposition_date(self): ...
    async def test_get_documents_due_for_review(self): ...
    async def test_get_documents_due_for_disposition(self): ...
```

### Integration Tests

```python
# tests/integration/test_document_control_api.py
class TestDocumentControlAPI:
    async def test_generate_document_number(self): ...
    async def test_create_revision(self): ...
    async def test_status_transition_with_validation(self): ...
    async def test_approval_workflow_complete_flow(self): ...
    async def test_periodic_review_completion(self): ...

# tests/integration/test_approval_workflow.py
class TestApprovalWorkflow:
    async def test_single_step_approval(self): ...
    async def test_multi_step_sequential_approval(self): ...
    async def test_rejection_returns_to_draft(self): ...
    async def test_skip_optional_step(self): ...
```

### Compliance Tests

```python
# tests/compliance/test_iso_document_control.py
class TestISODocumentControl:
    """Tests for ISO 9001 §7.5.2 and ISO 13485 §4.2.4-5 compliance."""

    async def test_document_number_uniqueness(self):
        """ISO 13485 §4.2.4: Documents must be uniquely identified."""

    async def test_approval_before_release(self):
        """ISO 9001 §7.5.2: Documents must be approved before release."""

    async def test_change_reason_required_for_major_revision(self):
        """ISO 13485 §4.2.5: Changes must be identified and controlled."""

    async def test_retention_policy_enforcement(self):
        """ISO 15489: Records must have defined retention periods."""

    async def test_supersession_tracking(self):
        """ISO 13485 §4.2.4: Prevent use of obsolete documents."""
```

---

## 12. Implementation Order

| Order | Component | Dependencies | Estimated Effort |
|-------|-----------|--------------|------------------|
| 1 | Database migrations | None | 2-3 hours |
| 2 | DocumentNumberSequence model & service | Migration 1, 2 | 3-4 hours |
| 3 | Page model additions | Migration 1 | 1-2 hours |
| 4 | DocumentStatus enum & transitions | Page model | 2-3 hours |
| 5 | RevisionService | Page model, transitions | 3-4 hours |
| 6 | RetentionPolicy model & service | Migration 3 | 3-4 hours |
| 7 | DocumentMetadataService | All models | 2-3 hours |
| 8 | ApprovalMatrix & ApprovalRecord models | Migration 4 | 2-3 hours |
| 9 | ApprovalService | Approval models | 4-5 hours |
| 10 | LifecycleConfig (configurable) | Transitions | 2-3 hours |
| 11 | API endpoints | All services | 4-5 hours |
| 12 | Unit tests | All components | 4-6 hours |
| 13 | Integration tests | APIs | 3-4 hours |
| 14 | Frontend components | APIs | 6-8 hours |

**Total: ~42-52 hours**

---

## Summary

Sprint 6 delivers:

1. **Document Lifecycle** - 5-state default (configurable per org)
2. **Document Numbering** - Org-level auto-increment with configurable format
3. **Revision Tracking** - Major (A→B) and minor (1.0→1.1) versions
4. **Approval Workflows** - Integrated with Change Requests from Sprint 4
5. **Retention Policies** - Configurable expiration actions and notifications
6. **Metadata Validation** - Required fields enforced on transitions
7. **Supersession Tracking** - Links between replaced documents
8. **Periodic Review** - Scheduled reviews with reminders

All features comply with ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, and ISO 15489.
