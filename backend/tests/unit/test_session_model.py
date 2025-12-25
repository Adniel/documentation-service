"""Unit tests for Session model (Sprint 5).

Tests session management for 21 CFR Part 11 compliance.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.db.models.session import (
    Session,
    DEFAULT_SESSION_TIMEOUT_MINUTES,
)


class TestSessionModel:
    """Tests for Session model."""

    def test_default_session_timeout(self):
        """Default timeout should be 30 minutes."""
        assert DEFAULT_SESSION_TIMEOUT_MINUTES == 30

    def test_create_session(self):
        """Should create a session with correct defaults."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert session.user_id == "user-123"
        assert session.token_jti == "jti-abc"
        assert session.ip_address == "192.168.1.1"
        assert session.user_agent == "Mozilla/5.0"
        assert session.is_active is True
        assert session.revoked_at is None
        assert session.revoked_reason is None

    def test_create_session_without_optional_fields(self):
        """Should create session without IP and user agent."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )

        assert session.user_id == "user-123"
        assert session.token_jti == "jti-abc"
        assert session.ip_address is None
        assert session.user_agent is None

    def test_create_session_custom_timeout(self):
        """Should create session with custom timeout."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            timeout_minutes=60,
        )

        # Check expires_at is roughly 60 minutes from now
        expected_min = datetime.utcnow() + timedelta(minutes=59)
        expected_max = datetime.utcnow() + timedelta(minutes=61)
        assert expected_min < session.expires_at < expected_max

    def test_is_valid_active_session(self):
        """Active, non-expired session should be valid."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            timeout_minutes=30,
        )

        assert session.is_valid() is True

    def test_is_valid_inactive_session(self):
        """Inactive session should not be valid."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )
        session.is_active = False

        assert session.is_valid() is False

    def test_is_valid_revoked_session(self):
        """Revoked session should not be valid."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )
        session.revoke("User logout")

        assert session.is_valid() is False

    def test_is_valid_expired_session(self):
        """Expired session should not be valid."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )
        # Set expires_at to the past
        session.expires_at = datetime.utcnow() - timedelta(minutes=1)

        assert session.is_valid() is False

    def test_refresh_updates_expiry(self):
        """Refresh should extend session expiry."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            timeout_minutes=10,  # Short timeout
        )
        original_expires = session.expires_at

        # Refresh with longer timeout
        session.refresh(timeout_minutes=60)

        # New expiry should be later than original
        assert session.expires_at > original_expires
        # Should be roughly 60 minutes from now
        expected_min = datetime.utcnow() + timedelta(minutes=59)
        assert session.expires_at > expected_min

    def test_refresh_updates_last_activity(self):
        """Refresh should update last_activity timestamp."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )
        original_activity = session.last_activity

        # Small delay to ensure different timestamp
        import time
        time.sleep(0.01)

        session.refresh()

        assert session.last_activity >= original_activity

    def test_revoke_sets_inactive(self):
        """Revoke should set session to inactive."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )

        session.revoke("User logout")

        assert session.is_active is False
        assert session.revoked_at is not None
        assert session.revoked_reason == "User logout"

    def test_revoke_with_custom_reason(self):
        """Revoke should store custom reason."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )

        session.revoke("Password changed - security measure")

        assert session.revoked_reason == "Password changed - security measure"

    def test_time_remaining_active_session(self):
        """Active session should have positive time remaining."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            timeout_minutes=30,
        )

        remaining = session.time_remaining_seconds
        # Should be close to 30 minutes (1800 seconds)
        assert 1700 < remaining <= 1800

    def test_time_remaining_expired_session(self):
        """Expired session should have 0 time remaining."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )
        session.expires_at = datetime.utcnow() - timedelta(minutes=5)

        assert session.time_remaining_seconds == 0

    def test_repr(self):
        """Session should have readable repr."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )

        repr_str = repr(session)
        assert "user_id=user-123" in repr_str
        assert "active=True" in repr_str
        assert "expires_at=" in repr_str


class TestSessionSecurityScenarios:
    """Tests for security-related session scenarios."""

    def test_session_invalidation_on_password_change(self):
        """Sessions should be revocable for password changes."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
        )

        # Simulate password change scenario
        session.revoke("Password changed - sessions revoked for security")

        assert session.is_valid() is False
        assert "Password changed" in session.revoked_reason

    def test_multiple_session_support(self):
        """Different JTIs should create independent sessions."""
        session1 = Session.create_session(
            user_id="user-123",
            token_jti="jti-session-1",
        )
        session2 = Session.create_session(
            user_id="user-123",
            token_jti="jti-session-2",
        )

        # Sessions are independent
        session1.revoke("Logout from device 1")

        assert session1.is_valid() is False
        assert session2.is_valid() is True

    def test_session_timeout_compliance(self):
        """Session timeout should meet 21 CFR Part 11 requirements.

        21 CFR §11.10(d) requires limiting system access to authorized
        individuals. Session timeout helps enforce this by invalidating
        inactive sessions.
        """
        # Create session with 30-minute timeout (configurable but reasonable default)
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            timeout_minutes=30,
        )

        # Session is valid initially
        assert session.is_valid() is True

        # Simulate 31 minutes passing
        session.expires_at = datetime.utcnow() - timedelta(minutes=1)

        # Session should now be invalid
        assert session.is_valid() is False

    def test_ip_address_tracking(self):
        """Session should track client IP for audit purposes."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            ip_address="203.0.113.42",
        )

        assert session.ip_address == "203.0.113.42"

    def test_user_agent_tracking(self):
        """Session should track user agent for audit purposes."""
        session = Session.create_session(
            user_id="user-123",
            token_jti="jti-abc",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        )

        assert "Mozilla" in session.user_agent
