"""Page renderer for converting TipTap JSON to HTML.

Sprint A: Publishing
"""

import html
import re
from typing import Any


class PageRenderer:
    """Renders TipTap JSON documents to HTML."""

    def __init__(self, base_path: str = ""):
        """Initialize renderer.

        Args:
            base_path: Base path for resolving relative links
        """
        self.base_path = base_path
        self.toc: list[dict[str, Any]] = []
        self.heading_counter = 0

    def render(self, content: dict[str, Any]) -> str:
        """Render TipTap document to HTML.

        Args:
            content: TipTap JSON document

        Returns:
            Rendered HTML string
        """
        self.toc = []
        self.heading_counter = 0

        if not content or content.get("type") != "doc":
            return ""

        html_parts = []
        for node in content.get("content", []):
            rendered = self._render_node(node)
            if rendered:
                html_parts.append(rendered)

        return "\n".join(html_parts)

    def get_toc(self) -> list[dict[str, Any]]:
        """Get table of contents from last render."""
        return self.toc

    def _render_node(self, node: dict[str, Any]) -> str:
        """Render a single node to HTML."""
        node_type = node.get("type", "")

        renderers = {
            "paragraph": self._render_paragraph,
            "heading": self._render_heading,
            "bulletList": self._render_bullet_list,
            "orderedList": self._render_ordered_list,
            "listItem": self._render_list_item,
            "codeBlock": self._render_code_block,
            "blockquote": self._render_blockquote,
            "horizontalRule": self._render_hr,
            "image": self._render_image,
            "table": self._render_table,
            "tableRow": self._render_table_row,
            "tableCell": self._render_table_cell,
            "tableHeader": self._render_table_header,
            "hardBreak": self._render_hard_break,
            "text": self._render_text,
            "taskList": self._render_task_list,
            "taskItem": self._render_task_item,
        }

        renderer = renderers.get(node_type)
        if renderer:
            return renderer(node)

        # Unknown node type - try to render children
        if "content" in node:
            return self._render_children(node)

        return ""

    def _render_children(self, node: dict[str, Any]) -> str:
        """Render all child nodes."""
        children = node.get("content", [])
        parts = [self._render_node(child) for child in children]
        return "".join(parts)

    def _render_paragraph(self, node: dict[str, Any]) -> str:
        """Render paragraph."""
        content = self._render_children(node)
        if not content.strip():
            return ""
        return f"<p>{content}</p>"

    def _render_heading(self, node: dict[str, Any]) -> str:
        """Render heading with anchor."""
        level = node.get("attrs", {}).get("level", 1)
        level = min(max(level, 1), 6)  # Clamp to 1-6

        content = self._render_children(node)
        if not content.strip():
            return ""

        # Generate unique ID for anchor
        self.heading_counter += 1
        heading_id = self._generate_id(content)

        # Add to TOC
        self.toc.append({
            "id": heading_id,
            "text": self._strip_html(content),
            "level": level,
        })

        return f'<h{level} id="{heading_id}">{content}</h{level}>'

    def _render_bullet_list(self, node: dict[str, Any]) -> str:
        """Render unordered list."""
        items = self._render_children(node)
        return f"<ul>{items}</ul>"

    def _render_ordered_list(self, node: dict[str, Any]) -> str:
        """Render ordered list."""
        start = node.get("attrs", {}).get("start", 1)
        items = self._render_children(node)
        if start != 1:
            return f'<ol start="{start}">{items}</ol>'
        return f"<ol>{items}</ol>"

    def _render_list_item(self, node: dict[str, Any]) -> str:
        """Render list item."""
        content = self._render_children(node)
        return f"<li>{content}</li>"

    def _render_task_list(self, node: dict[str, Any]) -> str:
        """Render task list (checkboxes)."""
        items = self._render_children(node)
        return f'<ul class="task-list">{items}</ul>'

    def _render_task_item(self, node: dict[str, Any]) -> str:
        """Render task item with checkbox."""
        checked = node.get("attrs", {}).get("checked", False)
        content = self._render_children(node)
        checkbox_attr = 'checked disabled' if checked else 'disabled'
        checkbox = f'<input type="checkbox" {checkbox_attr}>'
        return f'<li class="task-item">{checkbox} {content}</li>'

    def _render_code_block(self, node: dict[str, Any]) -> str:
        """Render code block with syntax highlighting class."""
        language = node.get("attrs", {}).get("language", "")
        content = self._render_children(node)
        content = html.escape(content)

        lang_class = f' class="language-{language}"' if language else ""
        return f'<pre><code{lang_class}>{content}</code></pre>'

    def _render_blockquote(self, node: dict[str, Any]) -> str:
        """Render blockquote."""
        content = self._render_children(node)
        return f"<blockquote>{content}</blockquote>"

    def _render_hr(self, node: dict[str, Any]) -> str:
        """Render horizontal rule."""
        return "<hr>"

    def _render_image(self, node: dict[str, Any]) -> str:
        """Render image."""
        attrs = node.get("attrs", {})
        src = attrs.get("src", "")
        alt = html.escape(attrs.get("alt", ""))
        title = attrs.get("title", "")

        if not src:
            return ""

        title_attr = f' title="{html.escape(title)}"' if title else ""
        return f'<img src="{html.escape(src)}" alt="{alt}"{title_attr}>'

    def _render_table(self, node: dict[str, Any]) -> str:
        """Render table."""
        content = self._render_children(node)
        return f'<table class="table">{content}</table>'

    def _render_table_row(self, node: dict[str, Any]) -> str:
        """Render table row."""
        content = self._render_children(node)
        return f"<tr>{content}</tr>"

    def _render_table_cell(self, node: dict[str, Any]) -> str:
        """Render table cell."""
        attrs = node.get("attrs", {})
        colspan = attrs.get("colspan", 1)
        rowspan = attrs.get("rowspan", 1)
        content = self._render_children(node)

        attr_str = ""
        if colspan > 1:
            attr_str += f' colspan="{colspan}"'
        if rowspan > 1:
            attr_str += f' rowspan="{rowspan}"'

        return f"<td{attr_str}>{content}</td>"

    def _render_table_header(self, node: dict[str, Any]) -> str:
        """Render table header cell."""
        attrs = node.get("attrs", {})
        colspan = attrs.get("colspan", 1)
        rowspan = attrs.get("rowspan", 1)
        content = self._render_children(node)

        attr_str = ""
        if colspan > 1:
            attr_str += f' colspan="{colspan}"'
        if rowspan > 1:
            attr_str += f' rowspan="{rowspan}"'

        return f"<th{attr_str}>{content}</th>"

    def _render_hard_break(self, node: dict[str, Any]) -> str:
        """Render hard break."""
        return "<br>"

    def _render_text(self, node: dict[str, Any]) -> str:
        """Render text with marks."""
        text = html.escape(node.get("text", ""))
        marks = node.get("marks", [])

        for mark in marks:
            mark_type = mark.get("type", "")
            attrs = mark.get("attrs", {})

            if mark_type == "bold":
                text = f"<strong>{text}</strong>"
            elif mark_type == "italic":
                text = f"<em>{text}</em>"
            elif mark_type == "code":
                text = f"<code>{text}</code>"
            elif mark_type == "strike":
                text = f"<del>{text}</del>"
            elif mark_type == "underline":
                text = f"<u>{text}</u>"
            elif mark_type == "link":
                href = html.escape(attrs.get("href", ""))
                target = attrs.get("target", "")
                target_attr = f' target="{target}"' if target else ""
                rel = ' rel="noopener noreferrer"' if target == "_blank" else ""
                text = f'<a href="{href}"{target_attr}{rel}>{text}</a>'
            elif mark_type == "highlight":
                color = attrs.get("color", "yellow")
                text = f'<mark style="background-color: {html.escape(color)}">{text}</mark>'
            elif mark_type == "subscript":
                text = f"<sub>{text}</sub>"
            elif mark_type == "superscript":
                text = f"<sup>{text}</sup>"

        return text

    def _generate_id(self, text: str) -> str:
        """Generate a URL-friendly ID from text."""
        # Strip HTML tags
        plain_text = self._strip_html(text)
        # Convert to lowercase
        slug = plain_text.lower()
        # Replace spaces with hyphens
        slug = re.sub(r"\s+", "-", slug)
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        # Remove consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        # Add counter for uniqueness
        return f"{slug}-{self.heading_counter}" if slug else f"heading-{self.heading_counter}"

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r"<[^>]+>", "", text)


def render_page_content(content: dict[str, Any], base_path: str = "") -> tuple[str, list[dict[str, Any]]]:
    """Convenience function to render page content.

    Args:
        content: TipTap JSON document
        base_path: Base path for resolving relative links

    Returns:
        Tuple of (rendered HTML, table of contents)
    """
    renderer = PageRenderer(base_path)
    html_content = renderer.render(content)
    return html_content, renderer.get_toc()
