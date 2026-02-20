"""Unit tests for Sprint G: ImportService and adapters.

Tests Markdown adapter, Confluence adapter, and import orchestration.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.portability.markdown_adapter import (
    MarkdownAdapter,
    _markdown_to_tiptap,
    _slugify,
    _title_from_filename,
)
from src.modules.portability.confluence_adapter import (
    ConfluenceAdapter,
    _html_to_tiptap,
    _extract_title_from_html,
)
from src.modules.portability.importer import ImportService
from src.modules.portability.schemas import ImportFormat, ImportItemStatus


class TestSlugify:
    """Test slug generation utility."""

    def test_basic(self):
        assert _slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert _slugify("Hello, World! #1") == "hello-world-1"

    def test_multiple_spaces(self):
        assert _slugify("hello   world") == "hello-world"

    def test_already_slug(self):
        assert _slugify("hello-world") == "hello-world"


class TestTitleFromFilename:
    """Test title derivation from filenames."""

    def test_basic(self):
        assert _title_from_filename("getting-started.md") == "Getting Started"

    def test_underscores(self):
        assert _title_from_filename("my_first_document.md") == "My First Document"


class TestMarkdownToTipTap:
    """Test Markdown to TipTap JSON conversion."""

    def test_heading(self):
        result = _markdown_to_tiptap("# Hello")
        assert result["content"][0]["type"] == "heading"
        assert result["content"][0]["attrs"]["level"] == 1

    def test_paragraph(self):
        result = _markdown_to_tiptap("Hello world")
        assert result["content"][0]["type"] == "paragraph"
        assert result["content"][0]["content"][0]["text"] == "Hello world"

    def test_code_block(self):
        result = _markdown_to_tiptap("```python\nprint('hi')\n```")
        assert result["content"][0]["type"] == "codeBlock"
        assert result["content"][0]["attrs"]["language"] == "python"

    def test_empty(self):
        result = _markdown_to_tiptap("")
        assert result["content"] == []

    def test_mixed_content(self):
        md = "# Title\n\nSome paragraph.\n\n## Subtitle\n\nAnother paragraph."
        result = _markdown_to_tiptap(md)
        assert len(result["content"]) == 4
        assert result["content"][0]["type"] == "heading"
        assert result["content"][1]["type"] == "paragraph"
        assert result["content"][2]["type"] == "heading"
        assert result["content"][3]["type"] == "paragraph"


class TestHTMLToTipTap:
    """Test HTML to TipTap JSON conversion."""

    def test_heading(self):
        result = _html_to_tiptap("<h1>Hello</h1>")
        assert result["content"][0]["type"] == "heading"
        assert result["content"][0]["attrs"]["level"] == 1

    def test_paragraph(self):
        result = _html_to_tiptap("<p>Hello world</p>")
        assert result["content"][0]["type"] == "paragraph"

    def test_code_block(self):
        result = _html_to_tiptap("<pre>print('hi')</pre>")
        assert result["content"][0]["type"] == "codeBlock"

    def test_skips_script(self):
        result = _html_to_tiptap("<script>alert('xss')</script><p>Safe</p>")
        texts = [
            c["content"][0]["text"]
            for c in result["content"]
            if c.get("content")
        ]
        assert "alert" not in " ".join(texts)


class TestExtractTitleFromHTML:
    """Test title extraction from HTML."""

    def test_from_title_tag(self):
        html = "<html><head><title>My Page</title></head><body></body></html>"
        assert _extract_title_from_html(html) == "My Page"

    def test_from_h1(self):
        html = "<body><h1>Getting Started</h1><p>Content</p></body>"
        assert _extract_title_from_html(html) == "Getting Started"

    def test_strips_confluence_suffix(self):
        html = "<title>My Page - Confluence Space</title>"
        assert _extract_title_from_html(html) == "My Page"


class TestMarkdownAdapter:
    """Test MarkdownAdapter file parsing."""

    def test_parse_folder(self, tmp_path):
        # Create test files
        (tmp_path / "getting-started.md").write_text("# Getting Started\n\nHello.")
        (tmp_path / "advanced-usage.md").write_text("# Advanced Usage\n\nDetails.")

        adapter = MarkdownAdapter()
        items = adapter.parse_folder(tmp_path)

        assert len(items) == 2
        assert all(i.item_type == "page" for i in items)
        assert all(i.status == ImportItemStatus.CREATE for i in items)

    def test_skips_underscore_files(self, tmp_path):
        (tmp_path / "normal.md").write_text("Content")
        (tmp_path / "_meta.yaml").write_text("title: Meta")

        adapter = MarkdownAdapter()
        items = adapter.parse_folder(tmp_path)

        assert len(items) == 1
        assert items[0].slug == "normal"

    def test_read_page_with_frontmatter(self, tmp_path):
        md = """---
title: Custom Title
slug: custom-slug
status: effective
diataxis_types:
  - tutorial
tags:
  - quality
---
# Content

Paragraph here.
"""
        (tmp_path / "test.md").write_text(md)

        adapter = MarkdownAdapter()
        content, meta = adapter.read_page(tmp_path / "test.md")

        assert meta.title == "Custom Title"
        assert meta.slug == "custom-slug"
        assert meta.status == "effective"
        assert meta.diataxis_types == ["tutorial"]
        assert content["content"][0]["type"] == "heading"

    def test_read_page_without_frontmatter(self, tmp_path):
        (tmp_path / "simple.md").write_text("# Simple Page\n\nJust text.")

        adapter = MarkdownAdapter()
        content, meta = adapter.read_page(tmp_path / "simple.md")

        assert meta.title == "Simple"
        assert meta.status == "draft"
        assert len(content["content"]) >= 1


class TestConfluenceAdapter:
    """Test ConfluenceAdapter file parsing."""

    def test_parse_export(self, tmp_path):
        (tmp_path / "Page One_12345.html").write_text(
            "<html><head><title>Page One</title></head>"
            "<body><h1>Page One</h1><p>Content.</p></body></html>"
        )
        (tmp_path / "Page Two_67890.html").write_text(
            "<html><head><title>Page Two</title></head>"
            "<body><h1>Page Two</h1><p>More content.</p></body></html>"
        )
        (tmp_path / "index.html").write_text("<html>Index</html>")

        adapter = ConfluenceAdapter()
        items = adapter.parse_export(tmp_path)

        # index.html should be skipped
        assert len(items) == 2
        assert all(i.item_type == "page" for i in items)

    def test_read_confluence_page(self, tmp_path):
        html = """<html>
<head><title>Inspection Procedure - QMS Space</title></head>
<body>
<h1>Inspection Procedure</h1>
<p>Step 1: Check the vials.</p>
<p>Step 2: Record results.</p>
<pre>example_code()</pre>
</body>
</html>"""
        (tmp_path / "test.html").write_text(html)

        adapter = ConfluenceAdapter()
        content, meta = adapter.read_page(tmp_path / "test.html")

        assert meta.title == "Inspection Procedure"
        assert meta.status == "draft"
        assert meta.classification == "internal"
        assert len(content["content"]) >= 3


class TestImportServiceFormatDetection:
    """Test import format detection."""

    def test_detect_docservice(self, tmp_path):
        export_dir = tmp_path / "export-acme"
        export_dir.mkdir()
        manifest = {"platform": "documentation-service", "format_version": "1.0"}
        (export_dir / "manifest.yaml").write_text(
            __import__("yaml").dump(manifest)
        )

        service = ImportService(AsyncMock())
        fmt = service.detect_format(tmp_path)
        assert fmt == ImportFormat.DOCSERVICE

    def test_detect_confluence(self, tmp_path):
        (tmp_path / "page.html").write_text(
            "<html><body>Confluence content</body></html>"
        )

        service = ImportService(AsyncMock())
        fmt = service.detect_format(tmp_path)
        assert fmt == ImportFormat.CONFLUENCE

    def test_detect_markdown(self, tmp_path):
        (tmp_path / "readme.md").write_text("# Hello")

        service = ImportService(AsyncMock())
        fmt = service.detect_format(tmp_path)
        assert fmt == ImportFormat.MARKDOWN

    def test_detect_markdown_when_both_exist(self, tmp_path):
        (tmp_path / "page.html").write_text("<html><body>Plain HTML content</body></html>")
        (tmp_path / "readme.md").write_text("# Hello")

        service = ImportService(AsyncMock())
        fmt = service.detect_format(tmp_path)
        # Markdown files present + HTML without confluence markers -> Markdown
        assert fmt == ImportFormat.MARKDOWN
