"""Acknowledgment service for training completions.

Integrates with the SignatureService to create compliant acknowledgments.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, 21 CFR Part 11 electronic signatures
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from uuid import uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import User, Page
from src.db.models.electronic_signature import SignatureMeaning
from src.db.models.signature_challenge import SignatureChallenge
from src.db.models.assessment import Assessment
from src.db.models.quiz_attempt import QuizAttempt, AttemptStatus
from src.db.models.learning_assignment import LearningAssignment, AssignmentStatus
from src.db.models.training_acknowledgment import TrainingAcknowledgment
from src.modules.document_control.signature_service import SignatureService, SignatureError
from src.modules.document_control.content_hash_service import compute_content_hash
from src.modules.audit.audit_service import AuditService
from src.modules.learning.schemas import (
    InitiateAcknowledgmentResponse,
    AcknowledgmentResponse,
    AcknowledgmentStatus,
)


class AcknowledgmentError(Exception):
    """Base exception for acknowledgment operations."""
    pass


class QuizNotPassedError(AcknowledgmentError):
    """Quiz required but not passed."""
    pass


class AlreadyAcknowledgedError(AcknowledgmentError):
    """Document already acknowledged by this user."""
    pass


class AcknowledgmentService:
    """Service for managing training acknowledgments."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.signature_service = SignatureService(db)
        self.audit = AuditService(db)

    async def get_acknowledgment_status(
        self,
        user: User,
        page_id: str,
    ) -> AcknowledgmentStatus:
        """Get the acknowledgment status for a user and page.

        Args:
            user: The user
            page_id: The page ID

        Returns:
            AcknowledgmentStatus with current state
        """
        # Get page
        page_result = await self.db.execute(
            select(Page).where(Page.id == page_id)
        )
        page = page_result.scalar_one_or_none()

        if not page:
            return AcknowledgmentStatus(
                page_id=page_id,
                has_valid_acknowledgment=False,
                requires_training=False,
                has_assessment=False,
                has_passed_quiz=False,
                can_acknowledge=False,
                reason="Page not found",
            )

        # Check for active assessment
        assessment = await self._get_active_assessment(page_id)

        # Check for valid acknowledgment
        acknowledgment = await self._get_valid_acknowledgment(user.id, page_id)

        # Check for passed quiz if assessment exists
        has_passed_quiz = False
        if assessment:
            passed_attempt = await self._get_passed_attempt(user.id, assessment.id)
            has_passed_quiz = passed_attempt is not None

        # Determine if user can acknowledge
        can_acknowledge = page.requires_training
        reason = None

        if not page.requires_training:
            can_acknowledge = False
            reason = "Page does not require training acknowledgment"
        elif acknowledgment and acknowledgment.is_currently_valid:
            can_acknowledge = False
            reason = "Already acknowledged and still valid"
        elif assessment and not has_passed_quiz:
            can_acknowledge = False
            reason = "Must pass assessment before acknowledging"

        return AcknowledgmentStatus(
            page_id=page_id,
            has_valid_acknowledgment=acknowledgment is not None and acknowledgment.is_currently_valid,
            acknowledgment=AcknowledgmentResponse.model_validate(acknowledgment) if acknowledgment else None,
            requires_training=page.requires_training,
            has_assessment=assessment is not None,
            has_passed_quiz=has_passed_quiz,
            can_acknowledge=can_acknowledge,
            reason=reason,
        )

    async def initiate_acknowledgment(
        self,
        user: User,
        page_id: str,
        quiz_attempt_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> InitiateAcknowledgmentResponse:
        """Initiate an acknowledgment flow.

        This creates a signature challenge that must be completed
        with password re-authentication.

        Args:
            user: User making the acknowledgment
            page_id: Page being acknowledged
            quiz_attempt_id: Optional quiz attempt ID
            assignment_id: Optional assignment ID
            ip_address: Client IP for audit

        Returns:
            InitiateAcknowledgmentResponse with challenge token

        Raises:
            QuizNotPassedError: If assessment required but not passed
            AlreadyAcknowledgedError: If already acknowledged
        """
        # Get page
        page_result = await self.db.execute(
            select(Page).where(Page.id == page_id)
        )
        page = page_result.scalar_one_or_none()

        if not page:
            raise AcknowledgmentError("Page not found")

        if not page.requires_training:
            raise AcknowledgmentError("Page does not require training acknowledgment")

        # Check for existing valid acknowledgment
        existing = await self._get_valid_acknowledgment(user.id, page_id)
        if existing and existing.is_currently_valid:
            raise AlreadyAcknowledgedError("You have already acknowledged this document")

        # Check assessment requirement
        assessment = await self._get_active_assessment(page_id)
        requires_quiz = assessment is not None
        quiz_passed = False

        if assessment:
            # Verify quiz attempt exists and passed
            if quiz_attempt_id:
                attempt_result = await self.db.execute(
                    select(QuizAttempt)
                    .where(
                        QuizAttempt.id == quiz_attempt_id,
                        QuizAttempt.user_id == user.id,
                        QuizAttempt.assessment_id == assessment.id,
                        QuizAttempt.status == AttemptStatus.PASSED.value,
                    )
                )
                passed_attempt = attempt_result.scalar_one_or_none()
            else:
                # Look for any passed attempt
                passed_attempt = await self._get_passed_attempt(user.id, assessment.id)

            if not passed_attempt:
                raise QuizNotPassedError(
                    "You must pass the assessment before acknowledging this document"
                )
            quiz_passed = True
            quiz_attempt_id = passed_attempt.id

        # Initiate signature challenge
        challenge, preview, title = await self.signature_service.initiate_signature(
            user=user,
            meaning=SignatureMeaning.ACKNOWLEDGED,
            page_id=page_id,
            reason=f"Training acknowledgment for: {page.title}",
            ip_address=ip_address,
        )

        # Store additional context in challenge (for complete_acknowledgment)
        # We'll retrieve this when completing

        return InitiateAcknowledgmentResponse(
            challenge_token=challenge.challenge_token,
            expires_at=challenge.expires_at,
            content_hash=challenge.content_hash,
            document_title=title,
            requires_quiz=requires_quiz,
            quiz_passed=quiz_passed if requires_quiz else None,
        )

    async def complete_acknowledgment(
        self,
        user: User,
        challenge_token: str,
        password: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> TrainingAcknowledgment:
        """Complete an acknowledgment with password re-authentication.

        Args:
            user: User completing the acknowledgment
            challenge_token: Token from initiate_acknowledgment
            password: User's password for re-authentication
            ip_address: Client IP
            user_agent: Client user agent
            session_id: Current session ID

        Returns:
            Created TrainingAcknowledgment

        Raises:
            SignatureError: If signature completion fails
        """
        # Get challenge to retrieve page_id
        challenge_result = await self.db.execute(
            select(SignatureChallenge)
            .where(SignatureChallenge.challenge_token == challenge_token)
        )
        challenge = challenge_result.scalar_one_or_none()

        if not challenge or challenge.user_id != user.id:
            raise SignatureError("Invalid challenge token")

        page_id = challenge.page_id
        if not page_id:
            raise SignatureError("Challenge not for a page")

        # Complete signature (handles re-auth)
        signature = await self.signature_service.complete_signature(
            challenge_token=challenge_token,
            password=password,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
        )

        # Get page for validity calculation
        page_result = await self.db.execute(
            select(Page).where(Page.id == page_id)
        )
        page = page_result.scalar_one()

        # Calculate valid_until
        valid_until = None
        if page.training_validity_months:
            valid_until = datetime.now(timezone.utc) + timedelta(
                days=page.training_validity_months * 30  # Approximate
            )

        # Find linked assignment if any
        assignment_id = None
        assignment_result = await self.db.execute(
            select(LearningAssignment)
            .where(
                LearningAssignment.page_id == page_id,
                LearningAssignment.user_id == user.id,
                LearningAssignment.status.in_([
                    AssignmentStatus.ASSIGNED.value,
                    AssignmentStatus.IN_PROGRESS.value,
                ]),
            )
            .order_by(LearningAssignment.assigned_at.desc())
            .limit(1)
        )
        assignment = assignment_result.scalar_one_or_none()
        if assignment:
            assignment_id = assignment.id
            assignment.mark_completed()

        # Find quiz attempt if any
        quiz_attempt_id = None
        assessment = await self._get_active_assessment(page_id)
        if assessment:
            passed_attempt = await self._get_passed_attempt(user.id, assessment.id)
            if passed_attempt:
                quiz_attempt_id = passed_attempt.id

        # Create acknowledgment
        acknowledgment = TrainingAcknowledgment(
            id=str(uuid4()),
            page_id=page_id,
            user_id=user.id,
            assignment_id=assignment_id,
            quiz_attempt_id=quiz_attempt_id,
            signature_id=signature.id,
            acknowledged_at=signature.signed_at,
            valid_until=valid_until,
            page_version=page.full_version,
            content_hash=signature.content_hash,
        )
        self.db.add(acknowledgment)

        # Log audit event
        await self.audit.log_event(
            event_type="learning.acknowledged",
            actor_id=user.id,
            actor_email=user.email,
            actor_ip=ip_address,
            resource_type="page",
            resource_id=page_id,
            resource_name=page.title,
            details={
                "acknowledgment_id": acknowledgment.id,
                "signature_id": signature.id,
                "valid_until": valid_until.isoformat() if valid_until else None,
                "assignment_id": assignment_id,
                "quiz_attempt_id": quiz_attempt_id,
            },
        )

        await self.db.flush()
        await self.db.refresh(acknowledgment)

        return acknowledgment

    async def get_acknowledgment(
        self,
        acknowledgment_id: str,
    ) -> Optional[TrainingAcknowledgment]:
        """Get an acknowledgment by ID."""
        result = await self.db.execute(
            select(TrainingAcknowledgment)
            .where(TrainingAcknowledgment.id == acknowledgment_id)
            .options(
                selectinload(TrainingAcknowledgment.page),
                selectinload(TrainingAcknowledgment.signature),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_acknowledgments(
        self,
        user_id: str,
        valid_only: bool = False,
    ) -> list[TrainingAcknowledgment]:
        """Get all acknowledgments for a user."""
        query = (
            select(TrainingAcknowledgment)
            .where(TrainingAcknowledgment.user_id == user_id)
            .options(selectinload(TrainingAcknowledgment.page))
            .order_by(TrainingAcknowledgment.acknowledged_at.desc())
        )

        if valid_only:
            query = query.where(TrainingAcknowledgment.is_valid == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def invalidate_acknowledgments_for_page(
        self,
        page_id: str,
        reason: str,
    ) -> int:
        """Invalidate all acknowledgments for a page.

        Called when a page is updated and requires re-training.

        Args:
            page_id: Page that was updated
            reason: Reason for invalidation

        Returns:
            Number of acknowledgments invalidated
        """
        result = await self.db.execute(
            select(TrainingAcknowledgment)
            .where(
                TrainingAcknowledgment.page_id == page_id,
                TrainingAcknowledgment.is_valid == True,
            )
        )
        acknowledgments = list(result.scalars().all())

        for ack in acknowledgments:
            ack.invalidate(reason)

            # Log audit event
            await self.audit.log_event(
                event_type="learning.acknowledgment_invalidated",
                actor_id=None,  # System action
                resource_type="training_acknowledgment",
                resource_id=ack.id,
                details={
                    "page_id": page_id,
                    "user_id": ack.user_id,
                    "reason": reason,
                },
            )

        await self.db.flush()

        return len(acknowledgments)

    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================

    async def _get_active_assessment(self, page_id: str) -> Optional[Assessment]:
        """Get active assessment for a page."""
        result = await self.db.execute(
            select(Assessment)
            .where(
                Assessment.page_id == page_id,
                Assessment.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def _get_valid_acknowledgment(
        self,
        user_id: str,
        page_id: str,
    ) -> Optional[TrainingAcknowledgment]:
        """Get a valid acknowledgment for user/page."""
        result = await self.db.execute(
            select(TrainingAcknowledgment)
            .where(
                TrainingAcknowledgment.user_id == user_id,
                TrainingAcknowledgment.page_id == page_id,
                TrainingAcknowledgment.is_valid == True,
            )
            .order_by(TrainingAcknowledgment.acknowledged_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_passed_attempt(
        self,
        user_id: str,
        assessment_id: str,
    ) -> Optional[QuizAttempt]:
        """Get a passed quiz attempt for user/assessment."""
        result = await self.db.execute(
            select(QuizAttempt)
            .where(
                QuizAttempt.user_id == user_id,
                QuizAttempt.assessment_id == assessment_id,
                QuizAttempt.status == AttemptStatus.PASSED.value,
            )
            .order_by(QuizAttempt.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
