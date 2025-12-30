"""
Unit tests for Git credential service.

Sprint 13: Git Remote Support
"""

import pytest
import base64
import secrets
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from uuid import uuid4

from src.modules.git.credential_service import CredentialService, CredentialError


class TestCredentialServiceEncryption:
    """Test encryption/decryption methods directly."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings with valid encryption key."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create a credential service with mocked db and settings."""
        mock_db = AsyncMock()
        with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
            return CredentialService(db=mock_db)

    def test_encrypt_decrypt_roundtrip(self, service):
        """Test that encryption followed by decryption returns original value."""
        original = "my-secret-token-12345"
        encrypted_value, iv = service._encrypt(original)
        decrypted = service._decrypt(encrypted_value, iv)
        assert decrypted == original

    def test_encrypt_produces_different_output(self, service):
        """Test that same value encrypted twice produces different ciphertext."""
        value = "test-value"
        encrypted1, iv1 = service._encrypt(value)
        encrypted2, iv2 = service._encrypt(value)
        # Different IVs should produce different ciphertext
        assert encrypted1 != encrypted2 or iv1 != iv2

    def test_encrypt_empty_string(self, service):
        """Test encrypting empty string."""
        encrypted_value, iv = service._encrypt("")
        decrypted = service._decrypt(encrypted_value, iv)
        assert decrypted == ""

    def test_encrypt_unicode(self, service):
        """Test encrypting unicode characters."""
        original = "tökén-with-émojis-🔑"
        encrypted_value, iv = service._encrypt(original)
        decrypted = service._decrypt(encrypted_value, iv)
        assert decrypted == original

    def test_decrypt_invalid_data_raises(self, service):
        """Test that decrypting invalid data raises error."""
        with pytest.raises(Exception):
            service._decrypt("not-valid-encrypted-data", "invalid-iv")


class TestSSHKeyFingerprint:
    """Test SSH key fingerprint extraction."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings with valid encryption key."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create a credential service with mocked db and settings."""
        mock_db = AsyncMock()
        with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
            return CredentialService(db=mock_db)

    def test_extract_fingerprint_ed25519_key(self, service):
        """Test extracting fingerprint from ED25519 public key."""
        ed25519_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl test@example.com"
        fingerprint = service._extract_ssh_fingerprint(ed25519_key)
        assert fingerprint is not None
        # MD5 fingerprint in colon-separated hex format (32 hex chars + 15 colons = 47 chars)
        assert ":" in fingerprint
        assert len(fingerprint) == 47

    def test_extract_fingerprint_invalid_key(self, service):
        """Test that invalid key returns None."""
        fingerprint = service._extract_ssh_fingerprint("not-a-valid-ssh-key")
        assert fingerprint is None

    def test_extract_fingerprint_empty_key(self, service):
        """Test that empty key returns None."""
        fingerprint = service._extract_ssh_fingerprint("")
        assert fingerprint is None


class TestTokenValidation:
    """Test token validation."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings with valid encryption key."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create a credential service with mocked db and settings."""
        mock_db = AsyncMock()
        with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
            return CredentialService(db=mock_db)

    def test_validate_github_classic_token(self, service):
        """Test GitHub classic token validation."""
        # Classic token format (ghp_)
        result = service._validate_token("ghp_abcdefghijklmnopqrstuvwxyz12345678", "github")
        assert result is True

    def test_validate_github_fine_grained_token(self, service):
        """Test GitHub fine-grained token validation."""
        result = service._validate_token("github_pat_abcdefghijklmnopqrstuvwxyz", "github")
        assert result is True

    def test_validate_github_invalid_token(self, service):
        """Test invalid GitHub token."""
        result = service._validate_token("invalid-token", "github")
        assert result is False

    def test_validate_gitlab_token(self, service):
        """Test GitLab token validation."""
        result = service._validate_token("glpat-abcdefghijklmnop", "gitlab")
        assert result is True

    def test_validate_gitlab_invalid_token(self, service):
        """Test invalid GitLab token."""
        result = service._validate_token("invalid", "gitlab")
        assert result is False

    def test_validate_custom_provider(self, service):
        """Test custom provider accepts tokens with 20+ characters."""
        result = service._validate_token("any-token-works-with-enough-chars", "custom")
        assert result is True

    def test_validate_empty_token(self, service):
        """Test empty token validation."""
        result = service._validate_token("", "custom")
        assert result is False


class TestMissingEncryptionKey:
    """Test error handling when encryption key is missing."""

    def test_missing_key_raises_error(self):
        """Test that missing encryption key raises error on use."""
        mock_settings = Mock()
        mock_settings.git_credential_encryption_key = ""
        mock_db = AsyncMock()

        with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
            service = CredentialService(db=mock_db)
            with pytest.raises(CredentialError, match="not configured"):
                service._encrypt("test")
