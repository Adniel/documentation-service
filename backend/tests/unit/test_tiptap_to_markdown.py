"""Unit tests for TipTap to Markdown converter."""

import pytest
from src.modules.content.tiptap_to_markdown import tiptap_to_markdown


class TestBasicConversion:
    """Tests for basic text and formatting conversion."""

    def test_empty_content(self):
        """Should return empty string for None input."""
        assert tiptap_to_markdown(None) == ""

    def test_empty_doc(self):
        """Should return empty string for empty document."""
        content = {"type": "doc", "content": []}
        assert tiptap_to_markdown(content) == ""

    def test_simple_paragraph(self):
        """Should convert simple paragraph."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello, world!"}],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "Hello, world!" in result

    def test_multiple_paragraphs(self):
        """Should convert multiple paragraphs with spacing."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "First paragraph"}],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Second paragraph"}],
                },
            ],
        }
        result = tiptap_to_markdown(content)
        assert "First paragraph" in result
        assert "Second paragraph" in result


class TestHeadings:
    """Tests for heading conversion."""

    def test_heading_level_1(self):
        """Should convert H1 heading."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Main Title"}],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "# Main Title" in result

    def test_heading_level_2(self):
        """Should convert H2 heading."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Section Title"}],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "## Section Title" in result

    def test_heading_level_3(self):
        """Should convert H3 heading."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Subsection"}],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "### Subsection" in result


class TestTextFormatting:
    """Tests for text formatting marks."""

    def test_bold_text(self):
        """Should convert bold text."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "This is "},
                        {
                            "type": "text",
                            "marks": [{"type": "bold"}],
                            "text": "bold",
                        },
                        {"type": "text", "text": " text"},
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "**bold**" in result

    def test_italic_text(self):
        """Should convert italic text."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "marks": [{"type": "italic"}],
                            "text": "italic",
                        }
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "*italic*" in result

    def test_strikethrough_text(self):
        """Should convert strikethrough text."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "marks": [{"type": "strike"}],
                            "text": "deleted",
                        }
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "~~deleted~~" in result

    def test_inline_code(self):
        """Should convert inline code."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "marks": [{"type": "code"}],
                            "text": "code",
                        }
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "`code`" in result

    def test_link(self):
        """Should convert link."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}],
                            "text": "Example",
                        }
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "[Example](https://example.com)" in result


class TestLists:
    """Tests for list conversion."""

    def test_bullet_list(self):
        """Should convert bullet list."""
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
                                    "content": [{"type": "text", "text": "Item 1"}],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Item 2"}],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_ordered_list(self):
        """Should convert ordered list."""
        content = {
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
                                    "content": [{"type": "text", "text": "First"}],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Second"}],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "1. First" in result
        assert "2. Second" in result

    def test_task_list(self):
        """Should convert task list."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "taskList",
                    "content": [
                        {
                            "type": "taskItem",
                            "attrs": {"checked": False},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Todo item"}],
                                }
                            ],
                        },
                        {
                            "type": "taskItem",
                            "attrs": {"checked": True},
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Done item"}],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "- [ ] Todo item" in result
        assert "- [x] Done item" in result


class TestCodeBlocks:
    """Tests for code block conversion."""

    def test_code_block_no_language(self):
        """Should convert code block without language."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {},
                    "content": [{"type": "text", "text": "print('hello')"}],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "```" in result
        assert "print('hello')" in result

    def test_code_block_with_language(self):
        """Should convert code block with language."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [{"type": "text", "text": "def hello():\n    pass"}],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "```python" in result
        assert "def hello():" in result


class TestBlockquotes:
    """Tests for blockquote conversion."""

    def test_simple_blockquote(self):
        """Should convert blockquote."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "A wise quote"}],
                        }
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "> A wise quote" in result


class TestTables:
    """Tests for table conversion."""

    def test_simple_table(self):
        """Should convert simple table."""
        content = {
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
                                            "content": [{"type": "text", "text": "Name"}],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableHeader",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [{"type": "text", "text": "Value"}],
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [{"type": "text", "text": "Item"}],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [{"type": "text", "text": "123"}],
                                        }
                                    ],
                                },
                            ],
                        },
                    ],
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "| Name | Value |" in result
        assert "| --- | --- |" in result
        assert "| Item | 123 |" in result


class TestMiscElements:
    """Tests for miscellaneous elements."""

    def test_horizontal_rule(self):
        """Should convert horizontal rule."""
        content = {
            "type": "doc",
            "content": [{"type": "horizontalRule"}],
        }
        result = tiptap_to_markdown(content)
        assert "---" in result

    def test_image(self):
        """Should convert image."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "image",
                    "attrs": {
                        "src": "https://example.com/image.png",
                        "alt": "Example image",
                    },
                }
            ],
        }
        result = tiptap_to_markdown(content)
        assert "![Example image](https://example.com/image.png)" in result


class TestComplexDocuments:
    """Tests for complex document structures."""

    def test_complete_document(self):
        """Should convert a complete document with various elements."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Getting Started"}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "This is a "},
                        {"type": "text", "marks": [{"type": "bold"}], "text": "guide"},
                        {"type": "text", "text": " to help you."},
                    ],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Prerequisites"}],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Python 3.9+"}],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Node.js 18+"}],
                                }
                            ],
                        },
                    ],
                },
            ],
        }
        result = tiptap_to_markdown(content)

        # Check all elements are present
        assert "# Getting Started" in result
        assert "**guide**" in result
        assert "## Prerequisites" in result
        assert "- Python 3.9+" in result
        assert "- Node.js 18+" in result
