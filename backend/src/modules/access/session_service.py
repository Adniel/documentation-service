"""Session management service for Sprint 5 Access Control.

Implements session tracking with configurable timeout for 21 CFR Part 11 compliance.
Sessions are validated on each request and refreshed on activity.

Compliance: 21 CFR §11.10(d) - Limiting system access to authorized individuals
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.session import Session, DEFAULT_SESSION_TIMEOUT_MINUTES
from src.db.models.user import User


class SessionService:
    """Service for managing user sessions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout_minutes: int = DEFAULT_SESSION_TIMEOUT_MINUTES,
    ) -> tuple[Session, str]:
        """Create a new session for a user.

        Returns:
            Tuple of (Session, token_jti) - the JTI should be included in JWT
        """
        token_jti = str(uuid.uuid4())

        session = Session.create_session(
            user_id=user_id,
            token_jti=token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            timeout_minutes=timeout_minutes,
        )

        self.db.add(session)
        await self.db.flush()

        return session, token_jti

    async def get_session_by_jti(self, token_jti: str) -> Optional[Session]:
        """Get a session by its JWT token ID."""
        result = await self.db.execute(
            select(Session).where(Session.token_jti == token_jti)
        )
        return result.scalar_one_or_none()

    async def validate_session(self, token_jti: str) -> tuple[bool, Optional[str]]:
        """Validate a session by its JWT token ID.

        Returns:
            Tuple of (is_valid, reason) - reason is set if invalid
        """
        session = await self.get_session_by_jti(token_jti)

        if not session:
            return False, "Session not found"

        if not session.is_active:
            return False, "Session has been revoked"

        if session.revoked_at is not None:
            return False, f"Session was revoked: {session.revoked_reason or 'Unknown reason'}"

        if datetime.utcnow() > session.expires_at:
            return False, "Session has expired due to inactivity"

        return True, None

    async def refresh_session(
        self,
        token_jti: str,
        timeout_minutes: int = DEFAULT_SESSION_TIMEOUT_MINUTES,
    ) -> bool:
        """Refresh a session's expiry time on activity.

        Returns:
            True if session was refreshed, False if session not found or invalid
        """
        session = await self.get_session_by_jti(token_jti)

        if not session or not session.is_valid():
            return False

        session.refresh(timeout_minutes)
        await self.db.flush()
        return True

    async def revoke_session(
        self,
        token_jti: str,
        reason: str = "User logout",
    ) -> bool:
        """Revoke a session (e.g., on logout).

        Returns:
            True if session was revoked, False if not found
        """
        session = await self.get_session_by_jti(token_jti)

        if not session:
            return False

        session.revoke(reason)
        await self.db.flush()
        return True

    async def revoke_all_user_sessions(
        self,
        user_id: str,
        reason: str = "All sessions revoked",
        exclude_jti: Optional[str] = None,
    ) -> int:
        """Revoke all active sessions for a user.

        Args:
            user_id: User whose sessions to revoke
            reason: Reason for revocation
            exclude_jti: Optional JTI to exclude (e.g., current session)

        Returns:
            Number of sessions revoked
        """
        now = datetime.utcnow()

        conditions = [
            Session.user_id == user_id,
            Session.is_active == True,
        ]
        if exclude_jti:
            conditions.append(Session.token_jti != exclude_jti)

        result = await self.db.execute(
            update(Session)
            .where(and_(*conditions))
            .values(
                is_active=False,
                revoked_at=now,
                revoked_reason=reason,
            )
        )

        await self.db.flush()
        return result.rowcount

    async def get_user_active_sessions(self, user_id: str) -> list[Session]:
        """Get all active sessions for a user."""
        result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.user_id == user_id,
                    Session.is_active == True,
                )
            ).order_by(Session.last_activity.desc())
        )
        return list(result.scalars().all())

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (can be run by a background task).

        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()

        result = await self.db.execute(
            update(Session)
            .where(
                and_(
                    Session.is_active == True,
                    Session.expires_at < now,
                )
            )
            .values(
                is_active=False,
                revoked_at=now,
                revoked_reason="Session expired due to inactivity",
            )
        )

        await self.db.flush()
        return result.rowcount

    async def get_session_info(self, token_jti: str) -> Optional[dict]:
        """Get session information for display.

        Returns:
            Dict with session info or None if not found
        """
        session = await self.get_session_by_jti(token_jti)

        if not session:
            return None

        return {
            "id": str(session.id),
            "user_id": session.user_id,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "expires_at": session.expires_at,
            "is_active": session.is_active,
            "is_valid": session.is_valid(),
            "time_remaining_seconds": session.time_remaining_seconds,
        }
