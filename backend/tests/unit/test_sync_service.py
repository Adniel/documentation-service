"""
Unit tests for Git sync service.

Sprint 13: Git Remote Support
"""

import pytest
import base64
import secrets
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime

from src.modules.git.sync_service import SyncService, SyncError


class TestSyncServiceInit:
    """Test SyncService initialization."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings with valid encryption key."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        mock.git_repos_path = "/tmp/test-repos"
        return mock

    def test_init_creates_service(self, mock_settings):
        """Test service initialization with dependencies."""
        mock_db = AsyncMock()
        with patch('src.modules.git.sync_service.get_git_service') as mock_git:
            with patch('src.modules.git.sync_service.CredentialService'):
                with patch('src.modules.git.sync_service.AuditService'):
                    with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                        service = SyncService(db=mock_db)
                        assert service is not None
                        assert service.db == mock_db


class TestGetOrganization:
    """Test organization retrieval."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        mock.git_repos_path = "/tmp/test-repos"
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create sync service with mocked dependencies."""
        mock_db = AsyncMock()

        with patch('src.modules.git.sync_service.get_git_service'):
            with patch('src.modules.git.sync_service.CredentialService'):
                with patch('src.modules.git.sync_service.AuditService'):
                    with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                        return SyncService(db=mock_db)

    @pytest.mark.asyncio
    async def test_get_organization_found(self, service):
        """Test getting organization when it exists."""
        org_id = uuid4()
        mock_org = Mock()
        mock_org.id = org_id
        mock_org.slug = "test-org"

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_org
        service.db.execute = AsyncMock(return_value=mock_result)

        org = await service.get_organization(str(org_id))

        assert org is not None
        assert org.slug == "test-org"

    @pytest.mark.asyncio
    async def test_get_organization_not_found(self, service):
        """Test getting organization when it doesn't exist."""
        org_id = uuid4()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        service.db.execute = AsyncMock(return_value=mock_result)

        org = await service.get_organization(str(org_id))

        assert org is None


class TestGetSyncStatus:
    """Test sync status retrieval."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        mock.git_repos_path = "/tmp/test-repos"
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create sync service with mocked dependencies."""
        mock_db = AsyncMock()

        with patch('src.modules.git.sync_service.get_git_service'):
            with patch('src.modules.git.sync_service.CredentialService'):
                with patch('src.modules.git.sync_service.AuditService'):
                    with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                        return SyncService(db=mock_db)

    @pytest.mark.asyncio
    async def test_get_sync_status_no_remote(self, service):
        """Test sync status when no remote is configured."""
        org_id = str(uuid4())
        mock_org = Mock()
        mock_org.git_remote_url = None
        mock_org.git_sync_enabled = False
        mock_org.git_sync_status = None
        mock_org.git_last_sync_at = None
        mock_org.git_default_branch = "main"
        mock_org.git_sync_strategy = None
        mock_org.git_remote_provider = None

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_org
        service.db.execute = AsyncMock(return_value=mock_result)

        status = await service.get_sync_status(org_id)

        assert status["sync_enabled"] is False
        assert status["remote_url"] is None

    @pytest.mark.asyncio
    async def test_get_sync_status_with_remote(self, service):
        """Test sync status when remote is configured."""
        org_id = str(uuid4())
        mock_org = Mock()
        mock_org.id = org_id
        mock_org.slug = "test-org"
        mock_org.git_remote_url = "git@github.com:owner/repo.git"
        mock_org.git_sync_enabled = True
        mock_org.git_sync_status = "synced"
        mock_org.git_last_sync_at = datetime.now()
        mock_org.git_default_branch = "main"
        mock_org.git_remote_provider = "github"
        mock_org.git_sync_strategy = "push_only"

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_org
        service.db.execute = AsyncMock(return_value=mock_result)

        # Mock git divergence
        service.git_service.get_divergence = Mock(return_value={
            "ahead": 0,
            "behind": 0,
            "remote_exists": True
        })

        status = await service.get_sync_status(org_id)

        assert status["sync_enabled"] is True
        assert status["remote_url"] == "git@github.com:owner/repo.git"
        assert status["sync_status"] == "synced"


class TestGetSyncHistory:
    """Test sync history retrieval."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        key = base64.b64encode(secrets.token_bytes(32)).decode()
        mock = Mock()
        mock.git_credential_encryption_key = key
        mock.git_repos_path = "/tmp/test-repos"
        return mock

    @pytest.fixture
    def service(self, mock_settings):
        """Create sync service with mocked dependencies."""
        mock_db = AsyncMock()

        with patch('src.modules.git.sync_service.get_git_service'):
            with patch('src.modules.git.sync_service.CredentialService'):
                with patch('src.modules.git.sync_service.AuditService'):
                    with patch('src.modules.git.credential_service.get_settings', return_value=mock_settings):
                        return SyncService(db=mock_db)

    @pytest.mark.asyncio
    async def test_get_sync_history_returns_events(self, service):
        """Test getting sync history returns formatted events."""
        org_id = uuid4()

        # Create mock event with enum-like attributes
        mock_event = Mock()
        mock_event.id = uuid4()
        mock_event.event_type = Mock()
        mock_event.event_type.value = "push"
        mock_event.direction = Mock()
        mock_event.direction.value = "outbound"
        mock_event.status = Mock()
        mock_event.status.value = "success"
        mock_event.branch_name = "main"
        mock_event.commit_sha_before = "abc123"
        mock_event.commit_sha_after = "def456"
        mock_event.error_message = None
        mock_event.trigger_source = "manual"
        mock_event.triggered_by_id = None
        mock_event.created_at = datetime.now()
        mock_event.started_at = datetime.now()
        mock_event.completed_at = datetime.now()
        mock_event.duration_seconds = 1.5

        # Mock queries - count query runs first, then events query
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1
        mock_events_result = Mock()
        mock_events_result.scalars.return_value.all.return_value = [mock_event]

        call_count = 0
        async def mock_execute(query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_count_result
            return mock_events_result

        service.db.execute = mock_execute

        result = await service.get_sync_history(org_id, limit=10)

        assert "events" in result
        assert "total" in result
        assert len(result["events"]) == 1
        assert result["events"][0]["event_type"] == "push"
        assert result["events"][0]["status"] == "success"
