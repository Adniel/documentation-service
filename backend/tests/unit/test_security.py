"""Unit tests for security module (Sprint 1)."""

import pytest
from datetime import datetime, timedelta, timezone

from src.modules.access.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_token_pair,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_returns_hash(self):
        """Password hashing should return a hash string."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_unique_hashes(self):
        """Same password should produce different hashes (salt)."""
        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # bcrypt uses random salt, so hashes should be different
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Correct password should verify successfully."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password should fail verification."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty(self):
        """Empty password should fail verification."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_hash_password_special_characters(self):
        """Password with special characters should hash correctly."""
        password = "P@$$w0rd!#%^&*()_+-=[]{}|;':\",./<>?"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Password with unicode characters should hash correctly."""
        password = "Lösenord123äöå"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token(self):
        """Access token should be created successfully."""
        user_id = "test-user-123"
        token = create_access_token(user_id)

        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

    def test_create_refresh_token(self):
        """Refresh token should be created successfully."""
        user_id = "test-user-123"
        token = create_refresh_token(user_id)

        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

    def test_decode_access_token(self):
        """Access token should decode with correct payload."""
        user_id = "test-user-123"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_decode_refresh_token(self):
        """Refresh token should decode with correct payload."""
        user_id = "test-user-123"
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """Invalid token should return None."""
        payload = decode_token("invalid.token.here")

        assert payload is None

    def test_decode_modified_token(self):
        """Modified token should fail to decode."""
        user_id = "test-user-123"
        token = create_access_token(user_id)
        # Modify the token
        modified_token = token[:-5] + "XXXXX"
        payload = decode_token(modified_token)

        assert payload is None

    def test_create_token_pair(self):
        """Token pair should contain both access and refresh tokens."""
        user_id = "test-user-123"
        access_token, refresh_token = create_token_pair(user_id)

        assert access_token is not None
        assert refresh_token is not None
        assert access_token != refresh_token

        # Verify both decode correctly
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"

    def test_access_token_expiration_type(self):
        """Access token should have correct expiration time."""
        user_id = "test-user-123"
        token = create_access_token(user_id)
        payload = decode_token(token)

        # exp should be in the future
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)

        assert exp_time > now
        # Access tokens typically expire in minutes (default 30)
        assert exp_time < now + timedelta(hours=2)

    def test_refresh_token_expiration_type(self):
        """Refresh token should have longer expiration time."""
        user_id = "test-user-123"
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        # exp should be in the future
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)

        assert exp_time > now
        # Refresh tokens typically expire in days (default 7)
        assert exp_time > now + timedelta(days=1)
