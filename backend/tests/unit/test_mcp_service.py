"""Unit tests for MCP service account management.

Sprint C: MCP Integration
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import hashlib

from src.modules.mcp.service import ServiceAccountService
from src.modules.mcp.schemas import ServiceAccountCreate, ServiceAccountUpdate


class TestServiceAccountService:
    """Test cases for ServiceAccountService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance with mock db."""
        return ServiceAccountService(mock_db)

    def test_generate_api_key(self, service):
        """Test API key generation."""
        full_key, key_hash, prefix = service.generate_api_key()

        # Key should have correct prefix
        assert full_key.startswith("dsk_")

        # Key should be sufficiently long
        assert len(full_key) >= 40

        # Prefix should match the key prefix
        assert full_key.startswith(prefix)

        # Hash should be valid SHA-256
        assert len(key_hash) == 64

        # Verifying hash works
        expected_hash = hashlib.sha256(full_key.encode()).hexdigest()
        assert key_hash == expected_hash

    def test_api_key_uniqueness(self, service):
        """Test that generated API keys are unique."""
        keys = set()
        for _ in range(100):
            full_key, _, _ = service.generate_api_key()
            assert full_key not in keys
            keys.add(full_key)

    @pytest.mark.asyncio
    async def test_create_service_account(self, service, mock_db):
        """Test service account creation."""
        data = ServiceAccountCreate(
            name="Test Account",
            description="Test description",
            role="reader",
            rate_limit_per_minute=100,
        )
        org_id = "org-123"
        user_id = "user-123"

        # Mock the flush and refresh
        async def mock_flush():
            pass

        async def mock_refresh(obj):
            obj.id = "account-123"

        mock_db.flush = mock_flush
        mock_db.refresh = mock_refresh

        account, api_key = await service.create(org_id, user_id, data)

        # Verify add was called
        mock_db.add.assert_called_once()

        # Verify API key format
        assert api_key.startswith("dsk_")

    @pytest.mark.asyncio
    async def test_get_by_api_key(self, service, mock_db):
        """Test retrieving account by API key."""
        # Create a test key
        test_key = "dsk_test_key_12345678901234567890"
        key_hash = hashlib.sha256(test_key.encode()).hexdigest()

        # Mock the database response
        mock_account = MagicMock()
        mock_account.api_key_hash = key_hash
        mock_account.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_account
        mock_db.execute.return_value = mock_result

        account = await service.get_by_api_key(test_key)

        assert account == mock_account

    @pytest.mark.asyncio
    async def test_get_by_api_key_not_found(self, service, mock_db):
        """Test retrieving account with invalid key."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        account = await service.get_by_api_key("dsk_invalid_key")

        assert account is None

    @pytest.mark.asyncio
    async def test_rotate_api_key(self, service, mock_db):
        """Test API key rotation."""
        mock_account = MagicMock()
        mock_account.api_key_hash = "old_hash"
        mock_account.api_key_prefix = "dsk_old_"

        updated_account, new_key = await service.rotate_api_key(mock_account)

        # New key should be generated
        assert new_key.startswith("dsk_")
        assert new_key != mock_account.api_key_hash

        # Account should be updated
        assert mock_account.api_key_hash != "old_hash"
        assert mock_account.api_key_prefix != "dsk_old_"

    def test_is_expired_not_set(self, service):
        """Test expiration check when no expiration is set."""
        mock_account = MagicMock()
        mock_account.expires_at = None

        assert not service.is_expired(mock_account)

    def test_is_expired_future_date(self, service):
        """Test expiration check with future date."""
        mock_account = MagicMock()
        mock_account.expires_at = datetime.utcnow() + timedelta(days=30)

        assert not service.is_expired(mock_account)

    def test_is_expired_past_date(self, service):
        """Test expiration check with past date."""
        mock_account = MagicMock()
        mock_account.expires_at = datetime.utcnow() - timedelta(days=1)

        assert service.is_expired(mock_account)

    def test_check_ip_allowed_no_restriction(self, service):
        """Test IP check with no allowlist."""
        mock_account = MagicMock()
        mock_account.ip_allowlist = None

        assert service.check_ip_allowed(mock_account, "192.168.1.1")

    def test_check_ip_allowed_empty_list(self, service):
        """Test IP check with empty allowlist."""
        mock_account = MagicMock()
        mock_account.ip_allowlist = []

        assert service.check_ip_allowed(mock_account, "192.168.1.1")

    def test_check_ip_allowed_exact_match(self, service):
        """Test IP check with exact match."""
        mock_account = MagicMock()
        mock_account.ip_allowlist = ["192.168.1.1", "10.0.0.1"]

        assert service.check_ip_allowed(mock_account, "192.168.1.1")
        assert service.check_ip_allowed(mock_account, "10.0.0.1")
        assert not service.check_ip_allowed(mock_account, "172.16.0.1")

    def test_check_ip_allowed_cidr(self, service):
        """Test IP check with CIDR notation."""
        mock_account = MagicMock()
        mock_account.ip_allowlist = ["192.168.1.0/24", "10.0.0.0/8"]

        assert service.check_ip_allowed(mock_account, "192.168.1.100")
        assert service.check_ip_allowed(mock_account, "10.255.255.255")
        assert not service.check_ip_allowed(mock_account, "172.16.0.1")

    @pytest.mark.asyncio
    async def test_update_service_account(self, service, mock_db):
        """Test updating service account."""
        mock_account = MagicMock()
        mock_account.name = "Old Name"
        mock_account.role = "reader"

        update_data = ServiceAccountUpdate(
            name="New Name",
            role="contributor",
        )

        updated = await service.update(mock_account, update_data)

        assert mock_account.name == "New Name"
        assert mock_account.role == "contributor"

    @pytest.mark.asyncio
    async def test_delete_service_account(self, service, mock_db):
        """Test deleting service account."""
        mock_account = MagicMock()

        await service.delete(mock_account)

        mock_db.delete.assert_called_once_with(mock_account)

    @pytest.mark.asyncio
    async def test_record_usage(self, service, mock_db):
        """Test recording usage."""
        await service.record_usage(
            account_id="account-123",
            operation="search_documents",
            response_code=200,
            ip_address="192.168.1.1",
            resource_id="doc-123",
            response_time_ms=50,
        )

        mock_db.add.assert_called_once()
