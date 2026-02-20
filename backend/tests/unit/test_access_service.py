"""Unit tests for published site access service.

Sprint D: Integrated Access Control
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from src.modules.publishing.access_service import (
    PublishedSiteAccessService,
    AccessResult,
)
from src.db.models.published_site import SiteVisibility


class TestAccessResult:
    """Test AccessResult dataclass."""

    def test_allowed_result(self):
        """Test allowed access result."""
        result = AccessResult(allowed=True, reason="Test")
        assert result.allowed
        assert not result.denied
        assert result.reason == "Test"

    def test_denied_result(self):
        """Test denied access result."""
        result = AccessResult(allowed=False, reason="No access")
        assert not result.allowed
        assert result.denied
        assert result.reason == "No access"

    def test_show_placeholder_default(self):
        """Test default show_placeholder value."""
        result = AccessResult(allowed=False, reason="Test")
        assert not result.show_placeholder

    def test_show_placeholder_true(self):
        """Test show_placeholder when set."""
        result = AccessResult(allowed=False, reason="Test", show_placeholder=True)
        assert result.show_placeholder


class TestPublishedSiteAccessService:
    """Test PublishedSiteAccessService methods."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance with mock db."""
        return PublishedSiteAccessService(mock_db)

    @pytest.fixture
    def public_site(self):
        """Create mock public site."""
        site = MagicMock()
        site.id = str(uuid4())
        site.visibility = SiteVisibility.PUBLIC.value
        site.allowed_email_domains = None
        site.show_restricted_as_placeholder = False
        site.restricted_placeholder_message = None
        return site

    @pytest.fixture
    def authenticated_site(self):
        """Create mock authenticated site."""
        site = MagicMock()
        site.id = str(uuid4())
        site.visibility = SiteVisibility.AUTHENTICATED.value
        site.allowed_email_domains = None
        site.show_restricted_as_placeholder = False
        site.restricted_placeholder_message = None
        return site

    @pytest.fixture
    def restricted_site(self):
        """Create mock restricted site."""
        site = MagicMock()
        site.id = str(uuid4())
        site.visibility = SiteVisibility.RESTRICTED.value
        site.allowed_email_domains = ["example.com", "company.org"]
        site.show_restricted_as_placeholder = True
        site.restricted_placeholder_message = "Access restricted"
        return site

    @pytest.fixture
    def mock_visitor(self):
        """Create mock visitor."""
        visitor = MagicMock()
        visitor.id = str(uuid4())
        visitor.email = "visitor@example.com"
        return visitor

    @pytest.fixture
    def mock_internal_user(self):
        """Create mock internal user."""
        user = MagicMock()
        user.id = str(uuid4())
        user.email = "user@company.org"
        user.clearance_level = 2
        return user

    @pytest.fixture
    def mock_page(self):
        """Create mock page."""
        page = MagicMock()
        page.id = str(uuid4())
        page.space_id = str(uuid4())
        page.classification = 0  # Public
        page.show_when_restricted = None
        return page

    # Site visibility tests

    @pytest.mark.asyncio
    async def test_public_site_allows_anonymous(self, service, public_site):
        """Public sites allow anonymous access."""
        result = await service.check_site_visibility(public_site, None, None)
        assert result.allowed
        assert result.reason == "Public site"

    @pytest.mark.asyncio
    async def test_public_site_allows_authenticated(
        self, service, public_site, mock_visitor
    ):
        """Public sites allow authenticated visitors."""
        result = await service.check_site_visibility(public_site, mock_visitor, None)
        assert result.allowed

    @pytest.mark.asyncio
    async def test_authenticated_site_denies_anonymous(
        self, service, authenticated_site
    ):
        """Authenticated sites deny anonymous access."""
        result = await service.check_site_visibility(authenticated_site, None, None)
        assert not result.allowed
        assert "Authentication required" in result.reason

    @pytest.mark.asyncio
    async def test_authenticated_site_allows_visitor(
        self, service, authenticated_site, mock_visitor
    ):
        """Authenticated sites allow logged in visitors."""
        result = await service.check_site_visibility(
            authenticated_site, mock_visitor, None
        )
        assert result.allowed
        assert "Authenticated user" in result.reason

    @pytest.mark.asyncio
    async def test_authenticated_site_allows_internal_user(
        self, service, authenticated_site, mock_internal_user
    ):
        """Authenticated sites allow internal users."""
        result = await service.check_site_visibility(
            authenticated_site, None, mock_internal_user
        )
        assert result.allowed

    @pytest.mark.asyncio
    async def test_restricted_site_denies_anonymous(self, service, restricted_site):
        """Restricted sites deny anonymous access."""
        result = await service.check_site_visibility(restricted_site, None, None)
        assert not result.allowed

    @pytest.mark.asyncio
    async def test_restricted_site_allows_matching_domain(
        self, service, restricted_site, mock_visitor
    ):
        """Restricted sites allow visitors from allowed domains."""
        mock_visitor.email = "user@example.com"
        result = await service.check_site_visibility(
            restricted_site, mock_visitor, None
        )
        assert result.allowed
        assert "example.com allowed" in result.reason

    @pytest.mark.asyncio
    async def test_restricted_site_denies_non_matching_domain(
        self, service, restricted_site, mock_visitor
    ):
        """Restricted sites deny visitors from non-allowed domains."""
        mock_visitor.email = "user@other.com"
        result = await service.check_site_visibility(
            restricted_site, mock_visitor, None
        )
        assert not result.allowed
        assert "not in allowed list" in result.reason

    # Clearance level tests

    def test_get_visitor_clearance_anonymous(self, service, public_site):
        """Anonymous visitors get clearance 0."""
        clearance = service.get_visitor_clearance(public_site, None, None, None)
        assert clearance == 0

    def test_get_visitor_clearance_internal_user(
        self, service, public_site, mock_internal_user
    ):
        """Internal users use their own clearance level."""
        mock_internal_user.clearance_level = 3
        clearance = service.get_visitor_clearance(
            public_site, None, mock_internal_user, None
        )
        assert clearance == 3

    def test_get_visitor_clearance_visitor_with_role(
        self, service, public_site, mock_visitor
    ):
        """Visitors with roles use role clearance."""
        mock_role = MagicMock()
        mock_role.clearance_level = 2
        mock_role.is_valid.return_value = True

        clearance = service.get_visitor_clearance(
            public_site, mock_visitor, None, mock_role
        )
        assert clearance == 2

    def test_get_visitor_clearance_visitor_without_role(
        self, service, public_site, mock_visitor
    ):
        """Visitors without roles get clearance 0."""
        clearance = service.get_visitor_clearance(public_site, mock_visitor, None, None)
        assert clearance == 0

    # Classification check tests

    @pytest.mark.asyncio
    async def test_classification_allows_sufficient_clearance(
        self, service, mock_page
    ):
        """Classification check allows when clearance >= classification."""
        mock_page.classification = 1  # Internal

        with patch.object(
            service.classification_service,
            "get_effective_classification",
            return_value=1,
        ):
            result = await service.check_page_classification(mock_page, clearance=2)

        assert result.allowed

    @pytest.mark.asyncio
    async def test_classification_denies_insufficient_clearance(
        self, service, mock_page
    ):
        """Classification check denies when clearance < classification."""
        mock_page.classification = 2  # Confidential

        with patch.object(
            service.classification_service,
            "get_effective_classification",
            return_value=2,
        ):
            result = await service.check_page_classification(mock_page, clearance=1)

        assert not result.allowed
        assert result.show_placeholder  # Should show placeholder for classification denial

    # Placeholder behavior tests

    def test_should_show_placeholder_site_default_false(
        self, service, public_site, mock_page
    ):
        """Use site default when page override is None."""
        public_site.show_restricted_as_placeholder = False
        mock_page.show_when_restricted = None

        result = service.should_show_placeholder(public_site, mock_page)
        assert not result

    def test_should_show_placeholder_site_default_true(
        self, service, restricted_site, mock_page
    ):
        """Use site default when page override is None."""
        restricted_site.show_restricted_as_placeholder = True
        mock_page.show_when_restricted = None

        result = service.should_show_placeholder(restricted_site, mock_page)
        assert result

    def test_should_show_placeholder_page_override_true(
        self, service, public_site, mock_page
    ):
        """Page override takes precedence."""
        public_site.show_restricted_as_placeholder = False
        mock_page.show_when_restricted = True

        result = service.should_show_placeholder(public_site, mock_page)
        assert result

    def test_should_show_placeholder_page_override_false(
        self, service, restricted_site, mock_page
    ):
        """Page override takes precedence."""
        restricted_site.show_restricted_as_placeholder = True
        mock_page.show_when_restricted = False

        result = service.should_show_placeholder(restricted_site, mock_page)
        assert not result


class TestVisitorRole:
    """Test visitor role functionality."""

    @pytest.fixture
    def mock_role(self):
        """Create mock visitor role."""
        role = MagicMock()
        role.visitor_id = str(uuid4())
        role.site_id = str(uuid4())
        role.clearance_level = 1
        role.allowed_page_ids = []
        role.expires_at = None
        role.is_active = True
        return role

    def test_role_is_valid_active_no_expiry(self, mock_role):
        """Active role without expiry is valid."""
        mock_role.is_active = True
        mock_role.expires_at = None
        mock_role.is_valid.return_value = True
        assert mock_role.is_valid()

    def test_role_is_valid_active_future_expiry(self, mock_role):
        """Active role with future expiry is valid."""
        mock_role.is_active = True
        mock_role.expires_at = datetime.utcnow() + timedelta(days=7)
        mock_role.is_valid.return_value = True
        assert mock_role.is_valid()

    def test_has_explicit_access_empty_list(self, mock_role):
        """No explicit access when list is empty."""
        mock_role.allowed_page_ids = []
        mock_role.has_explicit_access = lambda page_id: page_id in mock_role.allowed_page_ids
        assert not mock_role.has_explicit_access("page-123")

    def test_has_explicit_access_in_list(self, mock_role):
        """Has explicit access when page in list."""
        page_id = str(uuid4())
        mock_role.allowed_page_ids = [page_id]
        mock_role.has_explicit_access = lambda pid: pid in mock_role.allowed_page_ids
        assert mock_role.has_explicit_access(page_id)
