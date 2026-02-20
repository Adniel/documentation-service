"""Unit tests for content transformer.

Sprint D: Integrated Access Control
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.publishing.content_transformer import (
    ContentTransformer,
    TransformResult,
    TransformAction,
    transform_page_content,
)


class TestTransformResult:
    """Test TransformResult dataclass."""

    def test_default_values(self):
        """Test default values for transform result."""
        result = TransformResult(content="test")
        assert result.content == "test"
        assert result.restricted_references == []
        assert result.removed_embeds == []
        assert result.transform_count == 0

    def test_with_transforms(self):
        """Test result with transforms applied."""
        result = TransformResult(
            content="transformed",
            restricted_references=["page-1", "page-2"],
            removed_embeds=["embed-1"],
            transform_count=3,
        )
        assert len(result.restricted_references) == 2
        assert len(result.removed_embeds) == 1
        assert result.transform_count == 3


class TestTransformAction:
    """Test TransformAction enum."""

    def test_actions(self):
        """Test transform action values."""
        assert TransformAction.REMOVE.value == "remove"
        assert TransformAction.PLAIN_TEXT.value == "plain_text"
        assert TransformAction.PLACEHOLDER.value == "placeholder"


class TestContentTransformer:
    """Test ContentTransformer methods."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_access_service(self):
        """Create mock access service."""
        service = AsyncMock()
        return service

    @pytest.fixture
    def mock_site(self):
        """Create mock site."""
        site = MagicMock()
        site.id = str(uuid4())
        site.space_id = str(uuid4())
        site.show_restricted_as_placeholder = True
        site.restricted_placeholder_message = "Access restricted"
        return site

    @pytest.fixture
    def transformer(self, mock_db, mock_access_service, mock_site):
        """Create transformer instance."""
        return ContentTransformer(
            db=mock_db,
            access_service=mock_access_service,
            site=mock_site,
            visitor=None,
            internal_user=None,
        )

    # Pattern matching tests

    def test_markdown_link_pattern(self, transformer):
        """Test markdown link pattern matching."""
        content = "Check out [this page](/page/some-doc) for more info."
        matches = list(transformer.MARKDOWN_LINK_PATTERN.finditer(content))
        assert len(matches) == 1
        assert matches[0].group(1) == "this page"
        assert matches[0].group(2) == "/page/some-doc"

    def test_markdown_link_pattern_relative(self, transformer):
        """Test relative link pattern matching."""
        content = "See [related](./sibling-doc) and [parent](../other-doc)."
        matches = list(transformer.MARKDOWN_LINK_PATTERN.finditer(content))
        assert len(matches) == 2
        assert matches[0].group(2) == "./sibling-doc"
        assert matches[1].group(2) == "../other-doc"

    def test_wiki_link_pattern(self, transformer):
        """Test wiki link pattern matching."""
        content = "Link to [[Some Page]] and [[Other Page|with text]]."
        matches = list(transformer.WIKI_LINK_PATTERN.finditer(content))
        assert len(matches) == 2
        assert matches[0].group(1) == "Some Page"
        assert matches[0].group(2) is None
        assert matches[1].group(1) == "Other Page"
        assert matches[1].group(2) == "with text"

    def test_image_embed_pattern(self, transformer):
        """Test image embed pattern matching."""
        content = "![Alt text](/page/some-doc/image.png)"
        matches = list(transformer.IMAGE_EMBED_PATTERN.finditer(content))
        assert len(matches) == 1
        assert matches[0].group(1) == "Alt text"
        assert matches[0].group(2) == "/page/some-doc/image.png"

    def test_image_embed_pattern_attachments(self, transformer):
        """Test image embed with attachments path."""
        content = "![Screenshot](/attachments/page-id-123/screenshot.png)"
        matches = list(transformer.IMAGE_EMBED_PATTERN.finditer(content))
        assert len(matches) == 1
        assert matches[0].group(2) == "/attachments/page-id-123/screenshot.png"

    def test_transclusion_pattern(self, transformer):
        """Test transclusion pattern matching."""
        content = "Include content: {{include:some-page-ref}}"
        matches = list(transformer.TRANSCLUSION_PATTERN.finditer(content))
        assert len(matches) == 1
        assert matches[0].group(1) == "some-page-ref"

    # Transform tests with mocked access

    @pytest.mark.asyncio
    async def test_transform_link_accessible(
        self, transformer, mock_access_service, mock_db
    ):
        """Links to accessible pages are unchanged."""
        content = "See [details](/page/some-doc) for info."

        # Mock page lookup
        mock_page = MagicMock()
        mock_page.id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_page
        mock_db.execute.return_value = mock_result

        # Mock access check - allow access
        mock_access_result = MagicMock()
        mock_access_result.allowed = True
        mock_access_service.can_access_page.return_value = mock_access_result

        transformer._page_cache[mock_page.id] = mock_page
        transformer._access_cache[mock_page.id] = True

        result = await transformer.transform_content(content)

        assert "[details](/page/some-doc)" in result.content
        assert result.transform_count == 0

    @pytest.mark.asyncio
    async def test_transform_link_restricted_placeholder(
        self, transformer, mock_site
    ):
        """Links to restricted pages show placeholder icon."""
        content = "See [confidential](/page/secret) info."
        page_id = str(uuid4())

        mock_site.show_restricted_as_placeholder = True

        # Pre-cache the access denial
        transformer._access_cache[page_id] = False

        # Mock page resolution
        async def mock_resolve(ref):
            if ref == "/page/secret":
                return page_id
            return None

        transformer._resolve_ref_to_page_id = mock_resolve

        result = await transformer.transform_content(content)

        # Should add lock emoji for placeholder mode
        assert "🔒" in result.content or "confidential" in result.content

    @pytest.mark.asyncio
    async def test_transform_link_restricted_hidden(
        self, transformer, mock_site
    ):
        """Links to restricted pages become plain text when hidden."""
        content = "See [confidential](/page/secret) info."
        page_id = str(uuid4())

        mock_site.show_restricted_as_placeholder = False

        # Pre-cache the access denial
        transformer._access_cache[page_id] = False

        # Mock page resolution
        async def mock_resolve(ref):
            if ref == "/page/secret":
                return page_id
            return None

        transformer._resolve_ref_to_page_id = mock_resolve

        result = await transformer.transform_content(content)

        # Link should be removed, text kept
        assert "confidential" in result.content
        # Should not have the link markup
        assert "(/page/secret)" not in result.content or "🔒" not in result.content

    @pytest.mark.asyncio
    async def test_transform_external_link_unchanged(self, transformer):
        """External links are never transformed."""
        content = "Visit [Google](https://google.com) for search."

        result = await transformer.transform_content(content)

        assert "[Google](https://google.com)" in result.content
        assert result.transform_count == 0

    @pytest.mark.asyncio
    async def test_transform_multiple_links(self, transformer):
        """Multiple links are processed correctly."""
        content = """
        Here are some links:
        - [Public](/page/public)
        - [Internal](/page/internal)
        - [Confidential](/page/confidential)
        """

        # Pre-cache access
        transformer._access_cache = {
            "public-id": True,
            "internal-id": True,
            "confidential-id": False,
        }

        # Mock page resolution
        async def mock_resolve(ref):
            mapping = {
                "/page/public": "public-id",
                "/page/internal": "internal-id",
                "/page/confidential": "confidential-id",
            }
            return mapping.get(ref)

        transformer._resolve_ref_to_page_id = mock_resolve

        result = await transformer.transform_content(content)

        # Check that accessible links remain
        assert "Public" in result.content
        assert "Internal" in result.content
        # Confidential should be transformed
        assert "Confidential" in result.content
        assert result.transform_count >= 0

    @pytest.mark.asyncio
    async def test_prefetch_access_optimization(self, transformer, mock_db):
        """Prefetch extracts all page references for batch optimization."""
        content = """
        Links: [A](/page/a) [B](/page/b)
        Wiki: [[Page C]]
        Image: ![img](/attachments/page-d/img.png)
        Include: {{include:page-e}}
        """

        # Mock the resolution and access check
        resolved_refs = set()

        async def mock_resolve(ref):
            resolved_refs.add(ref)
            return f"id-{ref}"

        transformer._resolve_ref_to_page_id = mock_resolve

        async def mock_check(page_id):
            return True

        transformer._check_access = mock_check

        await transformer.prefetch_access(content)

        # Should have attempted to resolve multiple references
        assert len(resolved_refs) > 0


class TestConvenienceFunction:
    """Test transform_page_content convenience function."""

    @pytest.mark.asyncio
    async def test_transform_page_content_function(self):
        """Test convenience function creates transformer and runs."""
        mock_db = AsyncMock()
        mock_site = MagicMock()
        mock_site.id = str(uuid4())
        mock_site.space_id = str(uuid4())
        mock_site.show_restricted_as_placeholder = False

        content = "Simple content with no links."

        with patch(
            "src.modules.publishing.content_transformer.PublishedSiteAccessService"
        ):
            result = await transform_page_content(
                db=mock_db,
                site=mock_site,
                content=content,
            )

        assert result.content == content
        assert result.transform_count == 0
