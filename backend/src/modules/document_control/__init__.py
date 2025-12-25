"""Document Control module.

Sprint 6-7: ISO 9001/13485 and FDA 21 CFR Part 11 compliant document control.

This module provides:
- Document numbering service (auto-generate unique document numbers)
- Revision service (manage major/minor revisions)
- Lifecycle service (status transitions with validation)
- Retention service (periodic review and disposition tracking)
- Approval service (multi-step approval workflows)
- Metadata service (validation on transitions)
- Signature service (21 CFR Part 11 electronic signatures) [Sprint 7]
- NTP service (trusted timestamps for signatures) [Sprint 7]
- Content hash service (SHA-256 integrity verification) [Sprint 7]

Compliance:
- ISO 9001 §7.5.2 - Creating and updating documented information
- ISO 13485 §4.2.4 - Control of documents
- ISO 13485 §4.2.5 - Control of records
- ISO 15489 - Records management
- FDA 21 CFR Part 11 - Electronic signatures
"""

from src.modules.document_control.numbering_service import DocumentNumberingService
from src.modules.document_control.revision_service import RevisionService
from src.modules.document_control.lifecycle_service import LifecycleService
from src.modules.document_control.retention_service import RetentionService
from src.modules.document_control.approval_service import ApprovalService
from src.modules.document_control.metadata_service import DocumentMetadataService

# Sprint 7: Electronic Signatures
from src.modules.document_control.signature_service import (
    SignatureService,
    SignatureError,
    ChallengeExpiredError,
    ChallengeInvalidError,
    AuthenticationError,
    ContentChangedError,
)
from src.modules.document_control.ntp_service import (
    NTPService,
    NTPServiceError,
    get_trusted_timestamp,
)
from src.modules.document_control.content_hash_service import (
    compute_content_hash,
    verify_content_hash,
    ContentHashError,
)

__all__ = [
    # Sprint 6
    "DocumentNumberingService",
    "RevisionService",
    "LifecycleService",
    "RetentionService",
    "ApprovalService",
    "DocumentMetadataService",
    # Sprint 7: Electronic Signatures
    "SignatureService",
    "SignatureError",
    "ChallengeExpiredError",
    "ChallengeInvalidError",
    "AuthenticationError",
    "ContentChangedError",
    "NTPService",
    "NTPServiceError",
    "get_trusted_timestamp",
    "compute_content_hash",
    "verify_content_hash",
    "ContentHashError",
]
