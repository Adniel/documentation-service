"""Markdown folder import adapter.

Sprint G: Metadata Portability

Imports content from a Markdown folder structure into the platform.
Expected structure:
    folder/
    ├── page-title.md
    ├── subfolder/
    │   ├── another-page.md
    │   └── _meta.yaml  (optional)
    └── _meta.yaml  (optional)
"""

import re
from pathlib import Path
from typing import Any

import yaml

from src.modules.portability.schemas import (
    ImportItem,
    ImportItemStatus,
    PageMeta,
    SpaceMeta,
)


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def _title_from_filename(filename: str) -> str:
    """Derive a title from a filename."""
    name = Path(filename).stem
    return name.replace("-", " ").replace("_", " ").title()


def _markdown_to_tiptap(markdown_text: str) -> dict[str, Any]:
    """Convert Markdown text to basic TipTap JSON structure.

    This is a simplified converter that handles common Markdown elements.
    For full fidelity, a dedicated Markdown parser should be used.
    """
    content = []
    lines = markdown_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Headings
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            content.append({
                "type": "heading",
                "attrs": {"level": level},
                "content": [{"type": "text", "text": heading_match.group(2)}],
            })
            i += 1
            continue

        # Code blocks
        if line.startswith("```"):
            lang = line[3:].strip() or None
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            content.append({
                "type": "codeBlock",
                "attrs": {"language": lang},
                "content": [{"type": "text", "text": "\n".join(code_lines)}],
            })
            continue

        # Blank lines
        if not line.strip():
            i += 1
            continue

        # Regular paragraphs
        content.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": line}],
        })
        i += 1

    return {"type": "doc", "content": content} if content else {"type": "doc", "content": []}


class MarkdownAdapter:
    """Parses a folder of Markdown files for import."""

    def parse_folder(self, folder_path: Path) -> list[ImportItem]:
        """Scan a folder and return ImportItems for preview.

        Args:
            folder_path: Path to the root folder containing Markdown files

        Returns:
            List of ImportItems describing what would be imported
        """
        items: list[ImportItem] = []

        for md_file in sorted(folder_path.rglob("*.md")):
            if md_file.name.startswith("_"):
                continue  # skip metadata files

            rel = md_file.relative_to(folder_path)
            title = _title_from_filename(md_file.name)
            slug = _slugify(md_file.stem)

            # Check for sidecar _meta.yaml
            meta_path = md_file.parent / "_meta.yaml"
            if meta_path.exists():
                try:
                    meta_data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
                    if meta_data and isinstance(meta_data, dict):
                        title = meta_data.get("title", title)
                        slug = meta_data.get("slug", slug)
                except yaml.YAMLError:
                    pass

            items.append(ImportItem(
                path=str(rel),
                item_type="page",
                title=title,
                slug=slug,
                status=ImportItemStatus.CREATE,
            ))

        return items

    def read_page(self, file_path: Path) -> tuple[dict[str, Any], PageMeta]:
        """Read a Markdown file and return TipTap content + metadata.

        Args:
            file_path: Path to the .md file

        Returns:
            Tuple of (TipTap JSON content, PageMeta)
        """
        text = file_path.read_text(encoding="utf-8")

        # Extract YAML frontmatter if present
        frontmatter = {}
        body = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    pass
                body = parts[2].strip()

        title = frontmatter.get("title", _title_from_filename(file_path.name))
        slug = frontmatter.get("slug", _slugify(file_path.stem))

        meta = PageMeta(
            title=title,
            slug=slug,
            status=frontmatter.get("status", "draft"),
            classification=frontmatter.get("classification", "public"),
            diataxis_types=frontmatter.get("diataxis_types", []),
            summary=frontmatter.get("summary"),
            tags=frontmatter.get("tags", []),
        )

        content = _markdown_to_tiptap(body)
        return content, meta
