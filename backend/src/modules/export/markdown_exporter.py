"""Markdown exporter with YAML frontmatter.

Sprint I: Reader UI & Accessibility

Wraps the existing tiptap_to_markdown converter with frontmatter metadata.
"""

import io
import re
from typing import Any

import yaml

from src.modules.content.tiptap_to_markdown import tiptap_to_markdown


class MarkdownExporter:
    """Exports TipTap content as Markdown with YAML frontmatter."""

    @staticmethod
    def generate(
        tiptap_content: dict[str, Any],
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[io.BytesIO, str]:
        """Generate Markdown with frontmatter.

        Args:
            tiptap_content: TipTap JSON document
            title: Document title
            metadata: Optional metadata for frontmatter

        Returns:
            Tuple of (BytesIO buffer, suggested filename)
        """
        meta = metadata or {}

        # Build frontmatter
        frontmatter: dict[str, Any] = {"title": title}
        if meta.get("document_number"):
            frontmatter["document_number"] = meta["document_number"]
        if meta.get("version"):
            frontmatter["version"] = meta["version"]
        if meta.get("status"):
            frontmatter["status"] = meta["status"]
        if meta.get("author"):
            frontmatter["author"] = meta["author"]
        if meta.get("diataxis_types"):
            frontmatter["diataxis_types"] = meta["diataxis_types"]
        if meta.get("summary"):
            frontmatter["summary"] = meta["summary"]

        yaml_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        ).strip()

        # Convert content
        markdown_body = tiptap_to_markdown(tiptap_content)

        # Combine
        output = f"---\n{yaml_str}\n---\n\n{markdown_body}\n"

        buf = io.BytesIO(output.encode("utf-8"))
        buf.seek(0)

        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        filename = f"{slug}.md"

        return buf, filename
