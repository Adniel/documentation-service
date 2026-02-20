"""Unit tests for classification inheritance service.

Sprint D: Integrated Access Control
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.access.classification_service import (
    ClassificationService,
    ClassificationChain,
    CLASSIFICATION_NAMES,
    CLASSIFICATION_VALUES,
)


class TestClassificationChain:
    """Test ClassificationChain dataclass."""

    def test_effective_classification_from_page(self):
        """Page classification takes precedence."""
        chain = ClassificationChain(
            effective=3,
            organization=0,
            workspace=1,
            space=2,
            page=3,
            resolved_from="page",
        )
        assert chain.effective == 3
        assert chain.resolved_from == "page"

    def test_effective_classification_inheritance_from_space(self):
        """Falls back to space when page is None."""
        chain = ClassificationChain(
            effective=2,
            organization=0,
            workspace=1,
            space=2,
            page=None,
            resolved_from="space",
        )
        assert chain.effective == 2
        assert chain.resolved_from == "space"

    def test_effective_classification_inheritance_from_workspace(self):
        """Falls back to workspace when space is None."""
        chain = ClassificationChain(
            effective=1,
            organization=0,
            workspace=1,
            space=None,
            page=None,
            resolved_from="workspace",
        )
        assert chain.effective == 1
        assert chain.resolved_from == "workspace"

    def test_effective_classification_inheritance_from_org(self):
        """Falls back to org when all else is None."""
        chain = ClassificationChain(
            effective=2,
            organization=2,
            workspace=None,
            space=None,
            page=None,
            resolved_from="organization",
        )
        assert chain.effective == 2
        assert chain.resolved_from == "organization"

    def test_effective_classification_default_public(self):
        """Defaults to public (0) when no classification set."""
        chain = ClassificationChain(
            effective=0,
            organization=0,
            workspace=None,
            space=None,
            page=None,
            resolved_from="organization",
        )
        assert chain.effective == 0

    def test_effective_name_property(self):
        """Test effective_name property."""
        chain = ClassificationChain(
            effective=3,
            organization=0,
            workspace=1,
            space=2,
            page=3,
            resolved_from="page",
        )
        assert chain.effective_name == "restricted"

    def test_classification_names(self):
        """Test classification level names."""
        assert CLASSIFICATION_NAMES[0] == "public"
        assert CLASSIFICATION_NAMES[1] == "internal"
        assert CLASSIFICATION_NAMES[2] == "confidential"
        assert CLASSIFICATION_NAMES[3] == "restricted"

    def test_classification_values(self):
        """Test classification name to value mapping."""
        assert CLASSIFICATION_VALUES["public"] == 0
        assert CLASSIFICATION_VALUES["internal"] == 1
        assert CLASSIFICATION_VALUES["confidential"] == 2
        assert CLASSIFICATION_VALUES["restricted"] == 3


class TestClassificationService:
    """Test ClassificationService methods."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance with mock db."""
        return ClassificationService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create mock page with full hierarchy."""
        # Create organization
        org = MagicMock()
        org.id = str(uuid4())
        org.default_classification = 0

        # Create workspace
        workspace = MagicMock()
        workspace.id = str(uuid4())
        workspace.organization_id = org.id
        workspace.organization = org
        workspace.default_classification = None

        # Create space
        space = MagicMock()
        space.id = str(uuid4())
        space.workspace_id = workspace.id
        space.workspace = workspace
        space.classification = None

        # Create page
        page = MagicMock()
        page.id = str(uuid4())
        page.space_id = space.id
        page.space = space
        page.classification = None
        return page

    @pytest.mark.asyncio
    async def test_get_effective_classification_page_override(
        self, service, mock_page
    ):
        """Test page-level classification takes precedence."""
        mock_page.classification = "restricted"  # Pages use string classification

        result = await service.get_effective_classification(mock_page)

        assert result == 3  # restricted = 3

    @pytest.mark.asyncio
    async def test_get_effective_classification_inherits_from_space(
        self, service, mock_page
    ):
        """Test inheritance from space when page has no classification."""
        mock_page.classification = None
        mock_page.space.classification = 2  # Confidential

        result = await service.get_effective_classification(mock_page)

        assert result == 2

    @pytest.mark.asyncio
    async def test_get_effective_classification_inherits_from_workspace(
        self, service, mock_page
    ):
        """Test inheritance from workspace."""
        mock_page.classification = None
        mock_page.space.classification = None
        mock_page.space.workspace.default_classification = 1  # Internal

        result = await service.get_effective_classification(mock_page)

        assert result == 1

    @pytest.mark.asyncio
    async def test_get_effective_classification_inherits_from_org(
        self, service, mock_page
    ):
        """Test inheritance from organization."""
        mock_page.classification = None
        mock_page.space.classification = None
        mock_page.space.workspace.default_classification = None
        mock_page.space.workspace.organization.default_classification = 2

        result = await service.get_effective_classification(mock_page)

        assert result == 2

    def test_check_clearance_public_content(self, service):
        """Test clearance check for public content."""
        assert service.check_clearance(user_clearance=0, required_classification=0)
        assert service.check_clearance(user_clearance=1, required_classification=0)
        assert service.check_clearance(user_clearance=2, required_classification=0)
        assert service.check_clearance(user_clearance=3, required_classification=0)

    def test_check_clearance_internal_content(self, service):
        """Test clearance check for internal content."""
        assert not service.check_clearance(user_clearance=0, required_classification=1)
        assert service.check_clearance(user_clearance=1, required_classification=1)
        assert service.check_clearance(user_clearance=2, required_classification=1)
        assert service.check_clearance(user_clearance=3, required_classification=1)

    def test_check_clearance_confidential_content(self, service):
        """Test clearance check for confidential content."""
        assert not service.check_clearance(user_clearance=0, required_classification=2)
        assert not service.check_clearance(user_clearance=1, required_classification=2)
        assert service.check_clearance(user_clearance=2, required_classification=2)
        assert service.check_clearance(user_clearance=3, required_classification=2)

    def test_check_clearance_restricted_content(self, service):
        """Test clearance check for restricted content."""
        assert not service.check_clearance(user_clearance=0, required_classification=3)
        assert not service.check_clearance(user_clearance=1, required_classification=3)
        assert not service.check_clearance(user_clearance=2, required_classification=3)
        assert service.check_clearance(user_clearance=3, required_classification=3)

    def test_get_allowed_classifications_public_user(self, service):
        """Test allowed classifications for public clearance."""
        allowed = service.get_allowed_classifications(user_clearance=0)
        assert allowed == ["public"]

    def test_get_allowed_classifications_internal_user(self, service):
        """Test allowed classifications for internal clearance."""
        allowed = service.get_allowed_classifications(user_clearance=1)
        assert allowed == ["public", "internal"]

    def test_get_allowed_classifications_confidential_user(self, service):
        """Test allowed classifications for confidential clearance."""
        allowed = service.get_allowed_classifications(user_clearance=2)
        assert allowed == ["public", "internal", "confidential"]

    def test_get_allowed_classifications_restricted_user(self, service):
        """Test allowed classifications for restricted clearance."""
        allowed = service.get_allowed_classifications(user_clearance=3)
        assert allowed == ["public", "internal", "confidential", "restricted"]
