"""Unit tests for Diff service (Sprint 4).

Note: The diff service now outputs Markdown format instead of JSON
for better human readability in diff views.
"""

import pytest

from src.modules.content.diff_service import (
    _parse_unified_diff,
    _content_to_lines,
)
from src.modules.content.change_request_schemas import DiffHunk


class TestParseUnifiedDiff:
    """Tests for unified diff parsing."""

    def test_parse_empty_diff(self):
        """Empty diff should return empty hunks."""
        hunks, additions, deletions = _parse_unified_diff([])

        assert hunks == []
        assert additions == 0
        assert deletions == 0

    def test_parse_single_hunk(self):
        """Parse a single hunk with additions and deletions."""
        diff_lines = [
            "@@ -1,3 +1,4 @@",
            " line1",
            "-old line",
            "+new line",
            "+added line",
            " line3",
        ]

        hunks, additions, deletions = _parse_unified_diff(diff_lines)

        assert len(hunks) == 1
        assert hunks[0].old_start == 1
        assert hunks[0].old_lines == 3
        assert hunks[0].new_start == 1
        assert hunks[0].new_lines == 4
        assert additions == 2
        assert deletions == 1

    def test_parse_multiple_hunks(self):
        """Parse multiple hunks."""
        diff_lines = [
            "@@ -1,2 +1,2 @@",
            "-old1",
            "+new1",
            " context",
            "@@ -10,2 +10,3 @@",
            " more context",
            "+added",
            " end",
        ]

        hunks, additions, deletions = _parse_unified_diff(diff_lines)

        assert len(hunks) == 2
        assert hunks[0].old_start == 1
        assert hunks[1].old_start == 10
        assert additions == 2
        assert deletions == 1

    def test_parse_hunk_no_comma(self):
        """Parse hunk header without comma (single line)."""
        diff_lines = [
            "@@ -1 +1 @@",
            "-old",
            "+new",
        ]

        hunks, additions, deletions = _parse_unified_diff(diff_lines)

        assert len(hunks) == 1
        assert hunks[0].old_start == 1
        assert hunks[0].old_lines == 1
        assert hunks[0].new_start == 1
        assert hunks[0].new_lines == 1

    def test_parse_ignores_file_headers(self):
        """Parse should not count file headers as changes."""
        diff_lines = [
            "--- a/file.txt",
            "+++ b/file.txt",
            "@@ -1,2 +1,2 @@",
            " context",
            "-old",
            "+new",
        ]

        hunks, additions, deletions = _parse_unified_diff(diff_lines)

        # Should only count the actual change, not the --- and +++
        assert additions == 1
        assert deletions == 1

    def test_hunk_content_preserved(self):
        """Hunk content should be preserved."""
        diff_lines = [
            "@@ -1,3 +1,3 @@",
            " line1",
            "-old line",
            "+new line",
        ]

        hunks, _, _ = _parse_unified_diff(diff_lines)

        assert " line1\n" in hunks[0].content
        assert "-old line\n" in hunks[0].content
        assert "+new line\n" in hunks[0].content


class TestContentToLines:
    """Tests for content-to-lines conversion (now outputs Markdown)."""

    def test_none_content(self):
        """None content should return empty list."""
        result = _content_to_lines(None)
        assert result == []

    def test_simple_paragraph(self):
        """Simple paragraph content should produce Markdown text."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello world"}]
                }
            ]
        }
        result = _content_to_lines(content)
        markdown = "".join(result)

        assert "Hello world" in markdown

    def test_heading_content(self):
        """Heading content should produce Markdown heading."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "My Title"}]
                }
            ]
        }
        result = _content_to_lines(content)
        markdown = "".join(result)

        assert "# My Title" in markdown

    def test_formatted_text(self):
        """Formatted text should produce Markdown formatting."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "marks": [{"type": "bold"}], "text": "bold text"}
                    ]
                }
            ]
        }
        result = _content_to_lines(content)
        markdown = "".join(result)

        assert "**bold text**" in markdown

    def test_list_content(self):
        """List content should produce Markdown list."""
        content = {
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
                                    "content": [{"type": "text", "text": "Item 1"}]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        result = _content_to_lines(content)
        markdown = "".join(result)

        assert "- Item 1" in markdown

    def test_unicode_content(self):
        """Unicode content should be preserved in Markdown."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Tëst with ünïcödé"}]
                }
            ]
        }
        result = _content_to_lines(content)
        markdown = "".join(result)

        assert "ünïcödé" in markdown


class TestDiffResultSchema:
    """Tests for DiffResult schema."""

    def test_diff_hunk_schema(self):
        """DiffHunk should hold diff hunk data."""
        hunk = DiffHunk(
            old_start=10,
            old_lines=5,
            new_start=10,
            new_lines=7,
            content="-old\n+new\n",
        )

        assert hunk.old_start == 10
        assert hunk.old_lines == 5
        assert hunk.new_start == 10
        assert hunk.new_lines == 7
        assert "-old" in hunk.content


class TestDiffGeneration:
    """Tests for diff generation between content versions."""

    def test_diff_identical_content(self):
        """Identical content should produce identical lines."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Same content"}]
                }
            ]
        }
        lines1 = _content_to_lines(content)
        lines2 = _content_to_lines(content)

        # Same content should produce same lines
        assert lines1 == lines2

    def test_diff_different_content(self):
        """Different content should produce different lines."""
        content1 = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Original"}]
                }
            ]
        }
        content2 = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Modified"}]
                }
            ]
        }

        lines1 = _content_to_lines(content1)
        lines2 = _content_to_lines(content2)

        assert lines1 != lines2

    def test_diff_added_paragraph(self):
        """Adding a paragraph should show in diff."""
        content1 = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "First"}]
                }
            ]
        }
        content2 = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "First"}]
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Second"}]
                }
            ]
        }

        lines1 = _content_to_lines(content1)
        lines2 = _content_to_lines(content2)

        # New version should have more lines
        assert len(lines2) > len(lines1)

    def test_diff_removed_paragraph(self):
        """Removing a paragraph should show in diff."""
        content1 = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "First"}]
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Second"}]
                }
            ]
        }
        content2 = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "First"}]
                }
            ]
        }

        lines1 = _content_to_lines(content1)
        lines2 = _content_to_lines(content2)

        # Old version should have more lines
        assert len(lines1) > len(lines2)


class TestDiffEdgeCases:
    """Tests for edge cases in diff handling."""

    def test_empty_content(self):
        """Empty document should produce empty output."""
        content = {"type": "doc", "content": []}
        lines = _content_to_lines(content)

        assert lines == []

    def test_large_content(self):
        """Large content with many paragraphs should be handled."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": f"Paragraph {i}"}]
                }
                for i in range(50)
            ]
        }
        lines = _content_to_lines(content)

        # Should have lines for each paragraph
        assert len(lines) >= 50

    def test_code_block_content(self):
        """Code block content should be properly formatted."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [{"type": "text", "text": "def hello():\n    pass"}]
                }
            ]
        }
        lines = _content_to_lines(content)
        markdown = "".join(lines)

        assert "```python" in markdown
        assert "def hello():" in markdown

    def test_deeply_nested_lists(self):
        """Deeply nested list content should be formatted."""
        content = {
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
                                    "content": [{"type": "text", "text": "Level 1"}]
                                },
                                {
                                    "type": "bulletList",
                                    "content": [
                                        {
                                            "type": "listItem",
                                            "content": [
                                                {
                                                    "type": "paragraph",
                                                    "content": [{"type": "text", "text": "Level 2"}]
                                                }
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
        lines = _content_to_lines(content)
        markdown = "".join(lines)

        assert "Level 1" in markdown
        assert "Level 2" in markdown
