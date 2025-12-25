"""TipTap JSON to Markdown converter.

Converts TipTap editor JSON format to Markdown text for
human-readable diffs and export.
"""

from typing import Any


def _process_marks(text: str, marks: list[dict[str, Any]] | None) -> str:
    """Apply marks (bold, italic, etc.) to text."""
    if not marks:
        return text

    for mark in marks:
        mark_type = mark.get("type", "")
        if mark_type == "bold":
            text = f"**{text}**"
        elif mark_type == "italic":
            text = f"*{text}*"
        elif mark_type == "strike":
            text = f"~~{text}~~"
        elif mark_type == "code":
            text = f"`{text}`"
        elif mark_type == "link":
            href = mark.get("attrs", {}).get("href", "")
            text = f"[{text}]({href})"

    return text


def _process_content(content: list[dict[str, Any]] | None) -> str:
    """Process inline content (text, links, etc.)."""
    if not content:
        return ""

    result = []
    for node in content:
        node_type = node.get("type", "")

        if node_type == "text":
            text = node.get("text", "")
            marks = node.get("marks", [])
            result.append(_process_marks(text, marks))
        elif node_type == "hardBreak":
            result.append("  \n")
        else:
            # Unknown inline type - try to get text
            result.append(node.get("text", ""))

    return "".join(result)


def _process_node(node: dict[str, Any], indent: int = 0) -> list[str]:
    """Process a single TipTap node and return markdown lines."""
    node_type = node.get("type", "")
    attrs = node.get("attrs", {})
    content = node.get("content", [])
    lines = []

    if node_type == "doc":
        # Document root - process all children
        for child in content:
            lines.extend(_process_node(child, indent))

    elif node_type == "paragraph":
        text = _process_content(content)
        if text:
            lines.append(text)
        lines.append("")  # Empty line after paragraph

    elif node_type == "heading":
        level = attrs.get("level", 1)
        text = _process_content(content)
        lines.append(f"{'#' * level} {text}")
        lines.append("")

    elif node_type == "bulletList":
        for item in content:
            item_lines = _process_list_item(item, "- ", indent)
            lines.extend(item_lines)
        lines.append("")

    elif node_type == "orderedList":
        start = attrs.get("start", 1)
        for idx, item in enumerate(content):
            item_lines = _process_list_item(item, f"{start + idx}. ", indent)
            lines.extend(item_lines)
        lines.append("")

    elif node_type == "taskList":
        for item in content:
            checked = item.get("attrs", {}).get("checked", False)
            checkbox = "[x]" if checked else "[ ]"
            item_lines = _process_list_item(item, f"- {checkbox} ", indent)
            lines.extend(item_lines)
        lines.append("")

    elif node_type == "blockquote":
        for child in content:
            child_lines = _process_node(child, indent)
            for line in child_lines:
                if line:
                    lines.append(f"> {line}")
                else:
                    lines.append(">")
        lines.append("")

    elif node_type == "codeBlock":
        language = attrs.get("language", "")
        lines.append(f"```{language}")
        for child in content:
            if child.get("type") == "text":
                lines.append(child.get("text", ""))
        lines.append("```")
        lines.append("")

    elif node_type == "horizontalRule":
        lines.append("---")
        lines.append("")

    elif node_type == "table":
        table_lines = _process_table(content)
        lines.extend(table_lines)
        lines.append("")

    elif node_type == "image":
        src = attrs.get("src", "")
        alt = attrs.get("alt", "")
        title = attrs.get("title", "")
        if title:
            lines.append(f'![{alt}]({src} "{title}")')
        else:
            lines.append(f"![{alt}]({src})")
        lines.append("")

    else:
        # Unknown block type - try to extract text
        text = _process_content(content)
        if text:
            lines.append(text)
            lines.append("")

    return lines


def _process_list_item(item: dict[str, Any], prefix: str, indent: int = 0) -> list[str]:
    """Process a list item node."""
    lines = []
    content = item.get("content", [])
    indent_str = "  " * indent

    for idx, child in enumerate(content):
        if child.get("type") == "paragraph":
            text = _process_content(child.get("content", []))
            if idx == 0:
                lines.append(f"{indent_str}{prefix}{text}")
            else:
                lines.append(f"{indent_str}  {text}")
        elif child.get("type") in ("bulletList", "orderedList", "taskList"):
            # Nested list
            for nested_item in child.get("content", []):
                nested_prefix = "- " if child.get("type") == "bulletList" else "1. "
                nested_lines = _process_list_item(nested_item, nested_prefix, indent + 1)
                lines.extend(nested_lines)

    return lines


def _process_table(rows: list[dict[str, Any]]) -> list[str]:
    """Process a table node."""
    lines = []

    for row_idx, row in enumerate(rows):
        cells = row.get("content", [])
        cell_texts = []

        for cell in cells:
            cell_content = cell.get("content", [])
            cell_text = ""
            for para in cell_content:
                if para.get("type") == "paragraph":
                    cell_text += _process_content(para.get("content", []))
            cell_texts.append(cell_text)

        lines.append("| " + " | ".join(cell_texts) + " |")

        # Add header separator after first row
        if row_idx == 0:
            separator = "| " + " | ".join(["---"] * len(cell_texts)) + " |"
            lines.append(separator)

    return lines


def tiptap_to_markdown(content: dict[str, Any] | None) -> str:
    """Convert TipTap JSON document to Markdown.

    Args:
        content: TipTap JSON document (with type: "doc")

    Returns:
        Markdown string representation
    """
    if not content:
        return ""

    if content.get("type") != "doc":
        # Wrap in doc if needed
        content = {"type": "doc", "content": [content]}

    lines = _process_node(content)

    # Clean up multiple empty lines
    result = []
    prev_empty = False
    for line in lines:
        is_empty = not line.strip()
        if is_empty and prev_empty:
            continue
        result.append(line)
        prev_empty = is_empty

    # Remove trailing empty lines
    while result and not result[-1].strip():
        result.pop()

    return "\n".join(result)
