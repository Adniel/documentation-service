"""Audit service for creating immutable audit trail.

Implements audit logging for 21 CFR Part 11 and ISO 9001 compliance.

Compliance:
- 21 CFR §11.10(e) - Audit trail for changes
- ISO 9001 §7.5.3 - Control of documented information
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.audit import AuditEvent, AuditEventType
from src.modules.audit.audit_schemas import (
    AuditEventResponse,
    AuditEventListResponse,
    AuditStatsResponse,
    ChainVerificationResponse,
    EventVerificationResponse,
    ResourceAuditHistoryResponse,
)


class AuditService:
    """Service for creating and querying audit events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_event(
        self,
        event_type: AuditEventType | str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        actor_ip: Optional[str] = None,
        actor_user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditEvent:
        """Create an immutable audit event.

        Args:
            event_type: Type of event (from AuditEventType)
            actor_id: User ID who performed action
            actor_email: Email of actor (for historical record)
            actor_ip: IP address of actor
            actor_user_agent: User agent string
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            resource_name: Human-readable name of resource
            details: Additional event details

        Returns:
            Created AuditEvent
        """
        # Get previous hash for chain integrity
        previous_hash = await self._get_previous_hash()

        # Create event data for hashing
        event_type_str = event_type.value if isinstance(event_type, AuditEventType) else event_type
        timestamp = datetime.utcnow()

        event_data = {
            "event_type": event_type_str,
            "timestamp": timestamp.isoformat(),
            "actor_id": actor_id,
            "actor_email": actor_email,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "previous_hash": previous_hash,
        }

        # Calculate event hash
        event_hash = self._calculate_hash(event_data)

        # Create audit event
        audit_event = AuditEvent(
            event_type=event_type_str,
            timestamp=timestamp,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=actor_ip,
            actor_user_agent=actor_user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )

        self.db.add(audit_event)
        await self.db.flush()

        return audit_event

    async def _get_previous_hash(self) -> Optional[str]:
        """Get hash of the most recent audit event for chain integrity."""
        result = await self.db.execute(
            select(AuditEvent.event_hash)
            .order_by(desc(AuditEvent.timestamp))
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row

    def _calculate_hash(self, data: dict) -> str:
        """Calculate SHA-256 hash of event data."""
        # Sort keys for consistent hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    # -------------------------------------------------------------------------
    # Convenience methods for common event types
    # -------------------------------------------------------------------------

    async def log_login(
        self,
        user_id: str,
        user_email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None,
    ) -> AuditEvent:
        """Log login attempt."""
        event_type = AuditEventType.AUTH_LOGIN if success else AuditEventType.AUTH_FAILED
        details = {"success": success}
        if failure_reason:
            details["failure_reason"] = failure_reason

        return await self.log_event(
            event_type=event_type,
            actor_id=user_id if success else None,
            actor_email=user_email,
            actor_ip=ip_address,
            actor_user_agent=user_agent,
            resource_type="session",
            details=details,
        )

    async def log_logout(
        self,
        user_id: str,
        user_email: str,
        ip_address: Optional[str] = None,
        session_jti: Optional[str] = None,
    ) -> AuditEvent:
        """Log user logout."""
        return await self.log_event(
            event_type=AuditEventType.AUTH_LOGOUT,
            actor_id=user_id,
            actor_email=user_email,
            actor_ip=ip_address,
            resource_type="session",
            details={"session_jti": session_jti} if session_jti else None,
        )

    async def log_password_change(
        self,
        user_id: str,
        user_email: str,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log password change."""
        return await self.log_event(
            event_type=AuditEventType.AUTH_PASSWORD_CHANGED,
            actor_id=user_id,
            actor_email=user_email,
            actor_ip=ip_address,
            resource_type="user",
            resource_id=user_id,
        )

    async def log_access_granted(
        self,
        granted_by_id: str,
        granted_by_email: str,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: Optional[str] = None,
        role: str = "",
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log permission grant."""
        return await self.log_event(
            event_type=AuditEventType.ACCESS_GRANTED,
            actor_id=granted_by_id,
            actor_email=granted_by_email,
            actor_ip=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "target_user_id": user_id,
                "target_user_email": user_email,
                "role": role,
                "reason": reason,
            },
        )

    async def log_access_revoked(
        self,
        revoked_by_id: str,
        revoked_by_email: str,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: Optional[str] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log permission revocation."""
        return await self.log_event(
            event_type=AuditEventType.ACCESS_REVOKED,
            actor_id=revoked_by_id,
            actor_email=revoked_by_email,
            actor_ip=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "target_user_id": user_id,
                "target_user_email": user_email,
                "reason": reason,
            },
        )

    async def log_access_denied(
        self,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: Optional[str] = None,
        required_role: Optional[str] = None,
        user_role: Optional[str] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log access denial for security monitoring."""
        return await self.log_event(
            event_type=AuditEventType.ACCESS_DENIED,
            actor_id=user_id,
            actor_email=user_email,
            actor_ip=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "required_role": required_role,
                "user_role": user_role,
                "reason": reason,
            },
        )

    async def log_session_expired(
        self,
        user_id: str,
        session_jti: str,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log session expiration."""
        return await self.log_event(
            event_type=AuditEventType.AUTH_LOGOUT,
            actor_id=user_id,
            actor_ip=ip_address,
            resource_type="session",
            details={
                "session_jti": session_jti,
                "reason": "Session expired due to inactivity",
            },
        )

    async def log_clearance_change(
        self,
        changed_by_id: str,
        changed_by_email: str,
        user_id: str,
        user_email: str,
        previous_clearance: int,
        new_clearance: int,
        reason: str,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log clearance level change."""
        return await self.log_event(
            event_type=AuditEventType.ACCESS_GRANTED,  # Using ACCESS_GRANTED for clearance changes
            actor_id=changed_by_id,
            actor_email=changed_by_email,
            actor_ip=ip_address,
            resource_type="user_clearance",
            resource_id=user_id,
            details={
                "target_user_email": user_email,
                "previous_clearance": previous_clearance,
                "new_clearance": new_clearance,
                "reason": reason,
            },
        )

    # -------------------------------------------------------------------------
    # Content audit logging methods
    # -------------------------------------------------------------------------

    async def log_content_created(
        self,
        actor_id: str,
        actor_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        content_hash: Optional[str] = None,
        parent_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        """Log content creation (page, space, etc.)."""
        return await self.log_event(
            event_type=AuditEventType.CONTENT_CREATED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            actor_user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "content_hash": content_hash,
                "parent_id": parent_id,
            },
        )

    async def log_content_updated(
        self,
        actor_id: str,
        actor_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        reason: str,
        previous_hash: Optional[str] = None,
        new_hash: Optional[str] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        """Log content update with mandatory reason."""
        return await self.log_event(
            event_type=AuditEventType.CONTENT_UPDATED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            actor_user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "reason": reason,
                "previous_hash": previous_hash,
                "new_hash": new_hash,
                "changes": changes,
            },
        )

    async def log_content_deleted(
        self,
        actor_id: str,
        actor_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        reason: str,
        content_hash: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        """Log content deletion with mandatory reason."""
        return await self.log_event(
            event_type=AuditEventType.CONTENT_DELETED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            actor_user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "reason": reason,
                "content_hash": content_hash,
            },
        )

    async def log_content_viewed(
        self,
        actor_id: str,
        actor_email: str,
        resource_type: str,
        resource_id: str,
        resource_name: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log content view (optional, may generate high volume)."""
        return await self.log_event(
            event_type=AuditEventType.CONTENT_VIEWED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
        )

    # -------------------------------------------------------------------------
    # Workflow audit logging methods
    # -------------------------------------------------------------------------

    async def log_workflow_created(
        self,
        actor_id: str,
        actor_email: str,
        resource_id: str,
        resource_name: str,
        target_page_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log change request creation."""
        return await self.log_event(
            event_type="workflow.created",
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            resource_type="change_request",
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "target_page_id": target_page_id,
            },
        )

    async def log_workflow_submitted(
        self,
        actor_id: str,
        actor_email: str,
        resource_id: str,
        resource_name: str,
        content_hash: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log change request submission for review."""
        return await self.log_event(
            event_type=AuditEventType.WORKFLOW_SUBMITTED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            resource_type="change_request",
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "content_hash": content_hash,
            },
        )

    async def log_workflow_approved(
        self,
        actor_id: str,
        actor_email: str,
        resource_id: str,
        resource_name: str,
        signature_id: Optional[str] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log change request approval."""
        return await self.log_event(
            event_type=AuditEventType.WORKFLOW_APPROVED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            resource_type="change_request",
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "signature_id": signature_id,
                "reason": reason,
            },
        )

    async def log_workflow_rejected(
        self,
        actor_id: str,
        actor_email: str,
        resource_id: str,
        resource_name: str,
        reason: str,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log change request rejection with mandatory reason."""
        return await self.log_event(
            event_type=AuditEventType.WORKFLOW_REJECTED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            resource_type="change_request",
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "reason": reason,
            },
        )

    async def log_workflow_published(
        self,
        actor_id: str,
        actor_email: str,
        resource_id: str,
        resource_name: str,
        target_page_id: str,
        git_commit_sha: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Log change request publication/merge."""
        return await self.log_event(
            event_type=AuditEventType.WORKFLOW_PUBLISHED,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=ip_address,
            resource_type="change_request",
            resource_id=resource_id,
            resource_name=resource_name,
            details={
                "target_page_id": target_page_id,
                "git_commit_sha": git_commit_sha,
            },
        )

    # -------------------------------------------------------------------------
    # Query methods
    # -------------------------------------------------------------------------

    async def query_events(
        self,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> AuditEventListResponse:
        """Query audit events with filters."""
        # Build query conditions
        conditions = []
        if event_type:
            conditions.append(AuditEvent.event_type == event_type)
        if actor_id:
            conditions.append(AuditEvent.actor_id == actor_id)
        if resource_type:
            conditions.append(AuditEvent.resource_type == resource_type)
        if resource_id:
            conditions.append(AuditEvent.resource_id == resource_id)
        if start_date:
            conditions.append(AuditEvent.timestamp >= start_date)
        if end_date:
            conditions.append(AuditEvent.timestamp <= end_date)

        # Count total
        count_query = select(func.count(AuditEvent.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch events
        query = select(AuditEvent).order_by(desc(AuditEvent.timestamp))
        if conditions:
            query = query.where(and_(*conditions))
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        events = result.scalars().all()

        return AuditEventListResponse(
            events=[AuditEventResponse.model_validate(e) for e in events],
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + len(events)) < total,
        )

    async def get_event_by_id(self, event_id: str) -> Optional[AuditEvent]:
        """Get a single audit event by ID."""
        result = await self.db.execute(
            select(AuditEvent).where(AuditEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100,
    ) -> ResourceAuditHistoryResponse:
        """Get audit history for a specific resource."""
        result = await self.db.execute(
            select(AuditEvent)
            .where(
                and_(
                    AuditEvent.resource_type == resource_type,
                    AuditEvent.resource_id == resource_id,
                )
            )
            .order_by(desc(AuditEvent.timestamp))
            .limit(limit)
        )
        events = result.scalars().all()

        first_event = events[-1].timestamp if events else None
        last_event = events[0].timestamp if events else None
        resource_name = events[0].resource_name if events else None

        return ResourceAuditHistoryResponse(
            resource_type=resource_type,
            resource_id=UUID(resource_id),
            resource_name=resource_name,
            events=[AuditEventResponse.model_validate(e) for e in events],
            total_events=len(events),
            first_event=first_event,
            last_event=last_event,
        )

    async def get_stats(self) -> AuditStatsResponse:
        """Get audit trail statistics."""
        # Total events
        total_result = await self.db.execute(select(func.count(AuditEvent.id)))
        total_events = total_result.scalar() or 0

        # Events by type
        type_result = await self.db.execute(
            select(AuditEvent.event_type, func.count(AuditEvent.id))
            .group_by(AuditEvent.event_type)
        )
        events_by_type = {row[0]: row[1] for row in type_result}

        # Events today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await self.db.execute(
            select(func.count(AuditEvent.id))
            .where(AuditEvent.timestamp >= today_start)
        )
        events_today = today_result.scalar() or 0

        # Events this week
        week_start = today_start - timedelta(days=today_start.weekday())
        week_result = await self.db.execute(
            select(func.count(AuditEvent.id))
            .where(AuditEvent.timestamp >= week_start)
        )
        events_this_week = week_result.scalar() or 0

        # Unique actors
        actors_result = await self.db.execute(
            select(func.count(func.distinct(AuditEvent.actor_id)))
        )
        unique_actors = actors_result.scalar() or 0

        # Chain head
        chain_head_hash = await self._get_previous_hash()

        # Date range
        range_result = await self.db.execute(
            select(
                func.min(AuditEvent.timestamp),
                func.max(AuditEvent.timestamp),
            )
        )
        date_range = range_result.one_or_none()
        oldest_event = date_range[0] if date_range else None
        newest_event = date_range[1] if date_range else None

        return AuditStatsResponse(
            total_events=total_events,
            events_by_type=events_by_type,
            events_today=events_today,
            events_this_week=events_this_week,
            unique_actors=unique_actors,
            chain_head_hash=chain_head_hash,
            oldest_event=oldest_event,
            newest_event=newest_event,
        )

    # -------------------------------------------------------------------------
    # Verification methods (21 CFR §11.10(e) compliance)
    # -------------------------------------------------------------------------

    async def verify_chain_integrity(
        self,
        start_from_id: Optional[str] = None,
        end_at_id: Optional[str] = None,
        max_events: int = 10000,
    ) -> ChainVerificationResponse:
        """Verify hash chain integrity for tamper detection.

        Walks the audit chain and verifies each event's hash matches
        its content. Detects any modifications or deletions.

        Args:
            start_from_id: Start verification from this event (default: oldest)
            end_at_id: End verification at this event (default: newest)
            max_events: Maximum events to verify in one request

        Returns:
            ChainVerificationResponse with verification results
        """
        start_time = time.time()

        # Build query for events to verify
        query = select(AuditEvent).order_by(AuditEvent.timestamp)

        if start_from_id:
            start_event = await self.get_event_by_id(start_from_id)
            if start_event:
                query = query.where(AuditEvent.timestamp >= start_event.timestamp)

        if end_at_id:
            end_event = await self.get_event_by_id(end_at_id)
            if end_event:
                query = query.where(AuditEvent.timestamp <= end_event.timestamp)

        query = query.limit(max_events)

        result = await self.db.execute(query)
        events = result.scalars().all()

        if not events:
            return ChainVerificationResponse(
                is_valid=True,
                total_events=0,
                verified_events=0,
                verification_timestamp=datetime.utcnow(),
                chain_head_hash=None,
                verification_duration_ms=(time.time() - start_time) * 1000,
            )

        # Verify each event
        verified_count = 0
        first_invalid_id = None
        first_invalid_reason = None
        expected_previous_hash = None

        for i, event in enumerate(events):
            # Verify previous hash chain
            if i == 0:
                # First event - previous hash should be None or match stored
                expected_previous_hash = event.previous_hash
            else:
                # Check previous hash matches
                if event.previous_hash != expected_previous_hash:
                    first_invalid_id = UUID(str(event.id))
                    first_invalid_reason = (
                        f"Previous hash mismatch: expected {expected_previous_hash}, "
                        f"got {event.previous_hash}"
                    )
                    break

            # Verify event hash
            computed_hash = self._compute_event_hash(event)
            if computed_hash != event.event_hash:
                first_invalid_id = UUID(str(event.id))
                first_invalid_reason = (
                    f"Event hash mismatch: stored {event.event_hash}, "
                    f"computed {computed_hash}"
                )
                break

            verified_count += 1
            expected_previous_hash = event.event_hash

        # Get chain head
        chain_head_hash = await self._get_previous_hash()

        duration_ms = (time.time() - start_time) * 1000

        return ChainVerificationResponse(
            is_valid=first_invalid_id is None,
            total_events=len(events),
            verified_events=verified_count,
            first_invalid_event_id=first_invalid_id,
            first_invalid_reason=first_invalid_reason,
            verification_timestamp=datetime.utcnow(),
            chain_head_hash=chain_head_hash,
            verification_duration_ms=duration_ms,
        )

    async def verify_single_event(self, event_id: str) -> EventVerificationResponse:
        """Verify a single event's hash matches its content.

        Args:
            event_id: ID of the event to verify

        Returns:
            EventVerificationResponse with verification details
        """
        event = await self.get_event_by_id(event_id)
        if not event:
            return EventVerificationResponse(
                event_id=UUID(event_id),
                is_valid=False,
                stored_hash="",
                computed_hash="",
                previous_hash_valid=False,
                issues=["Event not found"],
            )

        issues = []

        # Compute hash
        computed_hash = self._compute_event_hash(event)
        hash_valid = computed_hash == event.event_hash

        if not hash_valid:
            issues.append(f"Hash mismatch: stored={event.event_hash}, computed={computed_hash}")

        # Check previous hash chain
        previous_hash_valid = True
        if event.previous_hash:
            # Find the event that should have this hash
            prev_result = await self.db.execute(
                select(AuditEvent)
                .where(AuditEvent.event_hash == event.previous_hash)
                .limit(1)
            )
            prev_event = prev_result.scalar_one_or_none()
            if not prev_event:
                previous_hash_valid = False
                issues.append(f"Previous hash {event.previous_hash} not found in chain")

        return EventVerificationResponse(
            event_id=UUID(str(event.id)),
            is_valid=hash_valid and previous_hash_valid,
            stored_hash=event.event_hash,
            computed_hash=computed_hash,
            previous_hash_valid=previous_hash_valid,
            issues=issues,
        )

    def _compute_event_hash(self, event: AuditEvent) -> str:
        """Recompute hash for an event to verify integrity."""
        event_data = {
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "actor_id": str(event.actor_id) if event.actor_id else None,
            "actor_email": event.actor_email,
            "resource_type": event.resource_type,
            "resource_id": str(event.resource_id) if event.resource_id else None,
            "details": event.details,
            "previous_hash": event.previous_hash,
        }
        return self._calculate_hash(event_data)

    async def get_chain_head(self) -> Optional[AuditEvent]:
        """Get the most recent audit event (chain head)."""
        result = await self.db.execute(
            select(AuditEvent)
            .order_by(desc(AuditEvent.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
