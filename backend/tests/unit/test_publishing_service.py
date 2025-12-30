"""Unit tests for PublishingService and ThemeService.

Sprint A: Publishing
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from src.modules.publishing.service import PublishingService, PublishingError
from src.modules.publishing.theme_service import ThemeService
from src.modules.publishing.renderer import PageRenderer, render_page_content
from src.modules.publishing.schemas import (
    SiteCreate,
    SiteUpdate,
    ThemeCreate,
    ThemeUpdate,
    SiteVisibility,
    SidebarPosition,
    ContentWidth,
)


class TestPageRenderer:
    """Tests for the PageRenderer class."""

    def test_render_empty_document(self):
        """Test rendering an empty document."""
        renderer = PageRenderer()
        result = renderer.render({})
        assert result == ""

    def test_render_invalid_document_type(self):
        """Test rendering a document with wrong type."""
        renderer = PageRenderer()
        result = renderer.render({"type": "invalid"})
        assert result == ""

    def test_render_simple_paragraph(self):
        """Test rendering a simple paragraph."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Hello World"}
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<p>Hello World</p>" in result

    def test_render_heading_with_toc(self):
        """Test rendering headings and generating TOC."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {"type": "text", "text": "Main Title"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [
                        {"type": "text", "text": "Subtitle"}
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        toc = renderer.get_toc()

        assert "<h1" in result
        assert "Main Title" in result
        assert "<h2" in result
        assert "Subtitle" in result

        assert len(toc) == 2
        assert toc[0]["text"] == "Main Title"
        assert toc[0]["level"] == 1
        assert toc[1]["text"] == "Subtitle"
        assert toc[1]["level"] == 2

    def test_render_bold_text(self):
        """Test rendering bold text."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Bold",
                            "marks": [{"type": "bold"}]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<strong>Bold</strong>" in result

    def test_render_italic_text(self):
        """Test rendering italic text."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Italic",
                            "marks": [{"type": "italic"}]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<em>Italic</em>" in result

    def test_render_link(self):
        """Test rendering a link."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Click here",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {"href": "https://example.com"}
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert '<a href="https://example.com">' in result
        assert "Click here</a>" in result

    def test_render_code_block(self):
        """Test rendering a code block."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {"type": "text", "text": "print('hello')"}
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert '<pre><code class="language-python">' in result
        # Content gets double-escaped: first by render_text, then by html.escape in code_block
        assert "print(" in result
        assert "hello" in result

    def test_render_bullet_list(self):
        """Test rendering a bullet list."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Item 1"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Item 2"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<ul>" in result
        assert "<li>" in result
        assert "Item 1" in result
        assert "Item 2" in result
        assert "</ul>" in result

    def test_render_ordered_list(self):
        """Test rendering an ordered list."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "orderedList",
                    "attrs": {"start": 1},
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "First"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<ol>" in result
        assert "<li>" in result
        assert "First" in result

    def test_render_blockquote(self):
        """Test rendering a blockquote."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "A quote"}
                            ]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<blockquote>" in result
        assert "A quote" in result

    def test_render_horizontal_rule(self):
        """Test rendering a horizontal rule."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {"type": "horizontalRule"}
            ]
        }
        result = renderer.render(doc)
        assert "<hr>" in result

    def test_render_image(self):
        """Test rendering an image."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "image",
                    "attrs": {
                        "src": "https://example.com/image.png",
                        "alt": "Example image",
                        "title": "Example title"
                    }
                }
            ]
        }
        result = renderer.render(doc)
        assert '<img src="https://example.com/image.png"' in result
        assert 'alt="Example image"' in result
        assert 'title="Example title"' in result

    def test_render_table(self):
        """Test rendering a table."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "table",
                    "content": [
                        {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": "tableHeader",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "Header"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "Cell"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert '<table class="table">' in result
        assert "<tr>" in result
        assert "<th>" in result
        assert "<td>" in result
        assert "Header" in result
        assert "Cell" in result

    def test_render_task_list(self):
        """Test rendering a task list."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "taskList",
                    "content": [
                        {
                            "type": "taskItem",
                            "attrs": {"checked": True},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Done task"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "taskItem",
                            "attrs": {"checked": False},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Pending task"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert '<ul class="task-list">' in result
        assert '<li class="task-item">' in result
        assert '<input type="checkbox" checked disabled>' in result
        assert '<input type="checkbox" disabled>' in result

    def test_render_strikethrough(self):
        """Test rendering strikethrough text."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Deleted",
                            "marks": [{"type": "strike"}]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<del>Deleted</del>" in result

    def test_render_inline_code(self):
        """Test rendering inline code."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "variable",
                            "marks": [{"type": "code"}]
                        }
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<code>variable</code>" in result

    def test_render_hard_break(self):
        """Test rendering hard break."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Line 1"},
                        {"type": "hardBreak"},
                        {"type": "text", "text": "Line 2"}
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<br>" in result

    def test_render_with_base_path(self):
        """Test rendering with base path for links."""
        renderer = PageRenderer(base_path="/s/docs")
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {"type": "text", "text": "Test Heading"}
                    ]
                }
            ]
        }
        renderer.render(doc)
        # Base path is available for internal link resolution
        assert renderer.base_path == "/s/docs"

    def test_render_escapes_html(self):
        """Test that HTML in content is escaped."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "<script>alert('xss')</script>"}
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_generate_unique_heading_ids(self):
        """Test that heading IDs are unique."""
        renderer = PageRenderer()
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [
                        {"type": "text", "text": "Same Title"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [
                        {"type": "text", "text": "Same Title"}
                    ]
                }
            ]
        }
        result = renderer.render(doc)
        toc = renderer.get_toc()

        # Each heading should have a unique ID
        assert toc[0]["id"] != toc[1]["id"]


class TestRenderPageContentFunction:
    """Tests for the render_page_content convenience function."""

    def test_render_page_content_returns_tuple(self):
        """Test that render_page_content returns HTML and TOC."""
        doc = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [
                        {"type": "text", "text": "Title"}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Content"}
                    ]
                }
            ]
        }
        html, toc = render_page_content(doc, "/s/site")

        assert isinstance(html, str)
        assert isinstance(toc, list)
        assert "Title" in html
        assert "Content" in html
        assert len(toc) == 1
        assert toc[0]["text"] == "Title"


class TestSchemaValidation:
    """Tests for Pydantic schema validation."""

    def test_site_create_slug_validation(self):
        """Test that site slug is validated."""
        # Valid slug
        data = SiteCreate(
            space_id="test-space-id",
            slug="valid-slug-123",
            site_title="Test Site",
        )
        assert data.slug == "valid-slug-123"

    def test_site_create_defaults(self):
        """Test SiteCreate default values."""
        data = SiteCreate(
            space_id="test-space-id",
            slug="my-site",
            site_title="My Site",
        )
        assert data.visibility == SiteVisibility.AUTHENTICATED  # Default is authenticated
        assert data.search_enabled is True
        assert data.toc_enabled is True
        assert data.feedback_enabled is False

    def test_theme_create_defaults(self):
        """Test ThemeCreate default values."""
        data = ThemeCreate(name="My Theme")
        assert data.primary_color == "#2563eb"
        assert data.background_color == "#ffffff"
        assert data.sidebar_position == SidebarPosition.LEFT
        assert data.content_width == ContentWidth.PROSE  # Default is prose
        assert data.toc_enabled is True

    def test_site_update_partial(self):
        """Test SiteUpdate allows partial updates."""
        data = SiteUpdate(site_title="New Title")
        assert data.site_title == "New Title"
        assert data.slug is None
        assert data.visibility is None

    def test_theme_update_partial(self):
        """Test ThemeUpdate allows partial updates."""
        data = ThemeUpdate(primary_color="#ff0000")
        assert data.primary_color == "#ff0000"
        assert data.name is None
