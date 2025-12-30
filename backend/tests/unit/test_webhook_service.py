"""
Unit tests for Git webhook service.

Sprint 13: Git Remote Support
"""

import pytest
import hmac
import hashlib
import json
import base64
import secrets
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from src.modules.git.webhook_service import WebhookService


class TestSignatureVerification:
    """Test webhook signature verification."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create webhook service with mocked dependencies."""
        mock_db = AsyncMock()
        with patch('src.modules.git.webhook_service.SyncService'):
            with patch('src.modules.git.webhook_service.AuditService'):
                with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                    return WebhookService(db=mock_db)

    def test_verify_github_signature_sha256_valid(self, service):
        """Test valid GitHub webhook signature with SHA256."""
        secret = "my-webhook-secret"
        payload = b'{"action": "push", "ref": "refs/heads/main"}'

        # Create valid signature with sha256= prefix
        signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        result = service.verify_github_signature(payload, signature, secret)
        assert result is True

    def test_verify_github_signature_invalid(self, service):
        """Test invalid GitHub webhook signature."""
        secret = "my-webhook-secret"
        payload = b'{"action": "push"}'
        invalid_signature = "sha256=invalid_signature_here"

        result = service.verify_github_signature(payload, invalid_signature, secret)
        assert result is False

    def test_verify_github_signature_wrong_secret(self, service):
        """Test GitHub signature with wrong secret."""
        payload = b'{"action": "push"}'

        # Create signature with one secret
        signature = "sha256=" + hmac.new(
            b"secret1",
            payload,
            hashlib.sha256
        ).hexdigest()

        # Verify with different secret
        result = service.verify_github_signature(payload, signature, "secret2")
        assert result is False

    def test_verify_gitlab_signature_valid(self, service):
        """Test valid GitLab webhook token."""
        secret = "my-gitlab-token"
        result = service.verify_gitlab_signature(secret, secret)
        assert result is True

    def test_verify_gitlab_signature_invalid(self, service):
        """Test invalid GitLab webhook token."""
        result = service.verify_gitlab_signature("wrong-token", "correct-token")
        assert result is False

    def test_verify_gitea_signature_valid(self, service):
        """Test valid Gitea webhook signature."""
        secret = "gitea-secret"
        payload = b'{"repository": {"name": "test"}}'

        # Gitea uses same format as GitHub
        signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        result = service.verify_gitea_signature(payload, signature, secret)
        assert result is True


class TestPushEventParsing:
    """Test push event parsing for different providers."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create webhook service with mocked dependencies."""
        mock_db = AsyncMock()
        with patch('src.modules.git.webhook_service.SyncService'):
            with patch('src.modules.git.webhook_service.AuditService'):
                with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                    return WebhookService(db=mock_db)

    def test_parse_github_push_event(self, service):
        """Test parsing GitHub push event."""
        payload = {
            "ref": "refs/heads/main",
            "before": "abc123",
            "after": "def456",
            "repository": {
                "full_name": "owner/repo",
                "clone_url": "https://github.com/owner/repo.git"
            },
            "pusher": {
                "name": "testuser",
                "email": "test@example.com"
            },
            "commits": [
                {"id": "def456", "message": "Test commit"}
            ]
        }

        result = service.parse_push_event("github", payload)

        assert result is not None
        assert result["branch"] == "main"
        assert result["before"] == "abc123"
        assert result["after"] == "def456"
        assert result["repository"] == "owner/repo"
        assert result["pusher"] == "testuser"

    def test_parse_gitlab_push_event(self, service):
        """Test parsing GitLab push event."""
        payload = {
            "ref": "refs/heads/develop",
            "before": "0000000000000000000000000000000000000000",
            "after": "abc123def456789",
            "project": {
                "path_with_namespace": "group/project"
            },
            "user_name": "Test User",
            "user_email": "test@gitlab.com",
            "commits": []
        }

        result = service.parse_push_event("gitlab", payload)

        assert result is not None
        assert result["branch"] == "develop"
        assert result["after"] == "abc123def456789"
        assert result["repository"] == "group/project"
        assert result["pusher"] == "Test User"

    def test_parse_gitea_push_event(self, service):
        """Test parsing Gitea push event."""
        payload = {
            "ref": "refs/heads/feature",
            "before": "111111",
            "after": "222222",
            "repository": {
                "full_name": "user/gitea-repo"
            },
            "pusher": {
                "username": "giteauser"
            },
            "commits": []
        }

        result = service.parse_push_event("gitea", payload)

        assert result is not None
        assert result["branch"] == "feature"
        assert result["before"] == "111111"
        assert result["after"] == "222222"
        assert result["repository"] == "user/gitea-repo"
        assert result["pusher"] == "giteauser"

    def test_parse_custom_push_event(self, service):
        """Test parsing custom provider push event."""
        payload = {
            "ref": "refs/heads/main",
            "before": "aaa",
            "after": "bbb",
        }

        result = service.parse_push_event("custom", payload)

        assert result is not None
        assert result["branch"] == "main"
        assert result["before"] == "aaa"
        assert result["after"] == "bbb"


class TestIsPushEvent:
    """Test push event detection."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create webhook service with mocked dependencies."""
        mock_db = AsyncMock()
        with patch('src.modules.git.webhook_service.SyncService'):
            with patch('src.modules.git.webhook_service.AuditService'):
                with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                    return WebhookService(db=mock_db)

    def test_is_push_event_github(self, service):
        """Test detecting push event from GitHub headers."""
        headers = {"x-github-event": "push"}
        assert service.is_push_event("github", headers) is True

    def test_is_push_event_github_not_push(self, service):
        """Test detecting non-push event from GitHub headers."""
        headers = {"x-github-event": "pull_request"}
        assert service.is_push_event("github", headers) is False

    def test_is_push_event_gitlab(self, service):
        """Test detecting push event from GitLab headers."""
        headers = {"x-gitlab-event": "Push Hook"}
        assert service.is_push_event("gitlab", headers) is True

    def test_is_push_event_gitea(self, service):
        """Test detecting push event from Gitea headers."""
        headers = {"x-gitea-event": "push"}
        assert service.is_push_event("gitea", headers) is True
