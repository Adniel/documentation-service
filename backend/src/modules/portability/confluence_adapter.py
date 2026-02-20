"""Confluence export import adapter.

Sprint G: Metadata Portability

Imports content from Confluence HTML space exports.
Confluence exports typically contain:
    export/
    ├── index.html          (space overview)
    ├── entities.xml        (metadata)
    └── pages/
        └── Page Title_12345.html
"""

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from src.modules.portability.schemas import (
    ImportItem,
    ImportItemStatus,
    PageMeta,
)


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:100]


class _HTMLTextExtractor(HTMLParser):
    """Extract clean text content from HTML."""

    def __init__(self):
        super().__init__()
        self._result: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "nav", "header", "footer"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "nav", "header", "footer"):
            self._skip = False
        if tag in ("p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
            self._result.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._result.append(data)

    def get_text(self) -> str:
        return "".join(self._result).strip()


class _HTMLToTipTapParser(HTMLParser):
    """Convert HTML to basic TipTap JSON structure."""

    def __init__(self):
        super().__init__()
        self.content: list[dict] = []
        self._current_text: list[str] = []
        self._current_tag: str | None = None
        self._in_skip = False
        self._heading_level: int = 0
        self._in_code = False
        self._code_text: list[str] = []

    def _flush_text(self) -> None:
        text = "".join(self._current_text).strip()
        if not text:
            self._current_text = []
            return

        if self._heading_level:
            self.content.append({
                "type": "heading",
                "attrs": {"level": self._heading_level},
                "content": [{"type": "text", "text": text}],
            })
        else:
            self.content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            })
        self._current_text = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "nav", "header", "footer"):
            self._in_skip = True
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_text()
            self._heading_level = int(tag[1])
        elif tag in ("p", "div"):
            self._flush_text()
        elif tag == "pre":
            self._flush_text()
            self._in_code = True
            self._code_text = []
        elif tag == "br":
            self._current_text.append("\n")
        elif tag == "li":
            self._flush_text()

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "nav", "header", "footer"):
            self._in_skip = False
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_text()
            self._heading_level = 0
        elif tag in ("p", "div", "li"):
            self._flush_text()
        elif tag == "pre":
            code = "".join(self._code_text).strip()
            if code:
                self.content.append({
                    "type": "codeBlock",
                    "attrs": {"language": None},
                    "content": [{"type": "text", "text": code}],
                })
            self._in_code = False

    def handle_data(self, data: str) -> None:
        if self._in_skip:
            return
        if self._in_code:
            self._code_text.append(data)
        else:
            self._current_text.append(data)

    def finalize(self) -> dict[str, Any]:
        self._flush_text()
        return {
            "type": "doc",
            "content": self.content if self.content else [],
        }


def _extract_title_from_html(html: str) -> str | None:
    """Extract <title> or first <h1> from HTML."""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if title_match:
        text = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        # Confluence titles often have " - Space Name" suffix
        text = re.split(r"\s*[-–—]\s*", text)[0].strip()
        if text:
            return text

    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if h1_match:
        return re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()

    return None


def _html_to_tiptap(html: str) -> dict[str, Any]:
    """Convert HTML string to TipTap JSON."""
    # Strip everything outside <body> if present
    body_match = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if body_match:
        html = body_match.group(1)

    parser = _HTMLToTipTapParser()
    parser.feed(html)
    return parser.finalize()


class ConfluenceAdapter:
    """Parses Confluence HTML exports for import."""

    def parse_export(self, export_path: Path) -> list[ImportItem]:
        """Scan a Confluence export folder and return ImportItems.

        Args:
            export_path: Path to extracted Confluence export

        Returns:
            List of ImportItems describing what would be imported
        """
        items: list[ImportItem] = []

        # Confluence exports HTML files (sometimes in subdirectories)
        for html_file in sorted(export_path.rglob("*.html")):
            if html_file.name.startswith("index"):
                continue

            rel = html_file.relative_to(export_path)
            html = html_file.read_text(encoding="utf-8", errors="replace")
            title = _extract_title_from_html(html) or _slugify(html_file.stem).replace("-", " ").title()
            slug = _slugify(title)

            items.append(ImportItem(
                path=str(rel),
                item_type="page",
                title=title,
                slug=slug,
                status=ImportItemStatus.CREATE,
            ))

        return items

    def read_page(self, file_path: Path) -> tuple[dict[str, Any], PageMeta]:
        """Read a Confluence HTML file and return TipTap content + metadata.

        Args:
            file_path: Path to the .html file

        Returns:
            Tuple of (TipTap JSON content, PageMeta)
        """
        html = file_path.read_text(encoding="utf-8", errors="replace")
        title = _extract_title_from_html(html) or _slugify(file_path.stem).replace("-", " ").title()
        slug = _slugify(title)

        content = _html_to_tiptap(html)

        meta = PageMeta(
            title=title,
            slug=slug,
            status="draft",
            classification="internal",
            diataxis_types=[],
        )

        return content, meta
