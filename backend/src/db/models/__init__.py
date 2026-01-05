"""Database models."""

from src.db.models.user import User
from src.db.models.organization import Organization
from src.db.models.workspace import Workspace
from src.db.models.space import Space
from src.db.models.page import Page, PageStatus
from src.db.models.audit import AuditEvent
from src.db.models.change_request import (
    ChangeRequest,
    ChangeRequestComment,
    ChangeRequestStatus,
)
from src.db.models.permission import (
    Permission,
    Role,
    ResourceType,
    ClassificationLevel,
    ROLE_CAPABILITIES,
)
from src.db.models.session import Session, DEFAULT_SESSION_TIMEOUT_MINUTES

# Sprint 6: Document Control models
from src.db.models.document_lifecycle import (
    DocumentStatus,
    DocumentType,
    LifecycleConfig,
    DEFAULT_DOCUMENT_PREFIXES,
    DEFAULT_TRANSITIONS,
    TRANSITION_PERMISSIONS,
)
from src.db.models.document_number import DocumentNumberSequence
from src.db.models.retention_policy import (
    RetentionPolicy,
    DispositionMethod,
    ExpirationAction,
)
from src.db.models.approval import (
    ApprovalMatrix,
    ApprovalRecord,
    ApprovalDecision,
)

# Sprint 7: Electronic Signatures
from src.db.models.electronic_signature import (
    ElectronicSignature,
    SignatureMeaning,
    SIGNATURE_MEANING_DESCRIPTIONS,
)
from src.db.models.signature_challenge import (
    SignatureChallenge,
    DEFAULT_CHALLENGE_EXPIRY_MINUTES,
)

# Sprint 9: Learning Module
from src.db.models.assessment import (
    Assessment,
    AssessmentQuestion,
    QuestionType,
)
from src.db.models.learning_assignment import (
    LearningAssignment,
    AssignmentStatus,
)
from src.db.models.quiz_attempt import (
    QuizAttempt,
    AttemptStatus,
)
from src.db.models.training_acknowledgment import TrainingAcknowledgment

# Sprint 13: Git Remote Support
from src.db.models.git_credential import (
    GitCredential,
    CredentialType,
)
from src.db.models.git_sync_event import (
    GitSyncEvent,
    SyncEventType,
    SyncDirection,
    SyncStatus,
)

# Sprint A: Publishing
from src.db.models.theme import (
    Theme,
    SidebarPosition,
    ContentWidth,
)
from src.db.models.published_site import (
    PublishedSite,
    SiteStatus,
    SiteVisibility,
)

# Sprint C: MCP Integration
from src.db.models.service_account import (
    ServiceAccount,
    ServiceAccountUsage,
)

__all__ = [
    # Core models
    "User",
    "Organization",
    "Workspace",
    "Space",
    "Page",
    "PageStatus",
    "AuditEvent",
    "ChangeRequest",
    "ChangeRequestComment",
    "ChangeRequestStatus",
    "Permission",
    "Role",
    "ResourceType",
    "ClassificationLevel",
    "ROLE_CAPABILITIES",
    "Session",
    "DEFAULT_SESSION_TIMEOUT_MINUTES",
    # Sprint 6: Document Control
    "DocumentStatus",
    "DocumentType",
    "LifecycleConfig",
    "DEFAULT_DOCUMENT_PREFIXES",
    "DEFAULT_TRANSITIONS",
    "TRANSITION_PERMISSIONS",
    "DocumentNumberSequence",
    "RetentionPolicy",
    "DispositionMethod",
    "ExpirationAction",
    "ApprovalMatrix",
    "ApprovalRecord",
    "ApprovalDecision",
    # Sprint 7: Electronic Signatures
    "ElectronicSignature",
    "SignatureMeaning",
    "SIGNATURE_MEANING_DESCRIPTIONS",
    "SignatureChallenge",
    "DEFAULT_CHALLENGE_EXPIRY_MINUTES",
    # Sprint 9: Learning Module
    "Assessment",
    "AssessmentQuestion",
    "QuestionType",
    "LearningAssignment",
    "AssignmentStatus",
    "QuizAttempt",
    "AttemptStatus",
    "TrainingAcknowledgment",
    # Sprint 13: Git Remote Support
    "GitCredential",
    "CredentialType",
    "GitSyncEvent",
    "SyncEventType",
    "SyncDirection",
    "SyncStatus",
    # Sprint A: Publishing
    "Theme",
    "SidebarPosition",
    "ContentWidth",
    "PublishedSite",
    "SiteStatus",
    "SiteVisibility",
    # Sprint C: MCP Integration
    "ServiceAccount",
    "ServiceAccountUsage",
]
