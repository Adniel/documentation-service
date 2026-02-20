"""PDF generator using WeasyPrint.

Sprint I: Reader UI & Accessibility
"""

import io
import re
from typing import Any


class PdfGenerator:
    """Generates PDF documents from rendered HTML content."""

    PRINT_CSS = """
    @page {
        size: A4;
        margin: 2.5cm 2cm;
        @top-right {
            content: counter(page) " / " counter(pages);
            font-size: 9pt;
            color: #666;
        }
        @bottom-center {
            content: string(doc-title);
            font-size: 8pt;
            color: #999;
        }
    }

    @page :first {
        @top-right { content: none; }
        @bottom-center { content: none; }
    }

    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #1a1a1a;
    }

    h1 { string-set: doc-title content(); }

    .title-page {
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
    }

    .title-page h1 {
        font-size: 28pt;
        margin-bottom: 0.5em;
        color: #111;
    }

    .title-page .metadata {
        font-size: 11pt;
        color: #666;
        margin-top: 2em;
    }

    .toc-page {
        page-break-after: always;
    }

    .toc-page h2 {
        font-size: 18pt;
        margin-bottom: 1em;
    }

    .toc-page ul {
        list-style: none;
        padding: 0;
    }

    .toc-page li {
        margin: 0.3em 0;
        line-height: 1.8;
    }

    .toc-page .toc-level-2 { padding-left: 1.5em; }
    .toc-page .toc-level-3 { padding-left: 3em; font-size: 10pt; }

    .toc-page a {
        color: #333;
        text-decoration: none;
    }

    h1 { font-size: 22pt; margin-top: 1.5em; }
    h2 { font-size: 16pt; margin-top: 1.2em; }
    h3 { font-size: 13pt; margin-top: 1em; }
    h4, h5, h6 { font-size: 11pt; margin-top: 1em; }

    pre {
        background: #f5f5f5;
        padding: 0.8em;
        border-radius: 4px;
        font-size: 9pt;
        overflow-x: hidden;
        white-space: pre-wrap;
        word-wrap: break-word;
        page-break-inside: avoid;
    }

    code {
        background: #f0f0f0;
        padding: 0.15em 0.3em;
        border-radius: 3px;
        font-size: 9.5pt;
    }

    pre code {
        background: none;
        padding: 0;
    }

    blockquote {
        border-left: 3px solid #ccc;
        padding-left: 1em;
        margin-left: 0;
        color: #555;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        page-break-inside: avoid;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 0.5em 0.8em;
        text-align: left;
        font-size: 10pt;
    }

    th { background: #f5f5f5; font-weight: 600; }

    img { max-width: 100%; }

    a { color: #2563eb; }

    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 1.5em 0;
    }
    """

    @staticmethod
    def generate(
        content_html: str,
        title: str,
        toc: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[io.BytesIO, str]:
        """Generate a PDF from rendered HTML.

        Args:
            content_html: Pre-rendered HTML content
            title: Document title
            toc: Table of contents entries
            metadata: Optional metadata (author, version, date, etc.)

        Returns:
            Tuple of (BytesIO buffer, suggested filename)
        """
        from weasyprint import HTML

        meta = metadata or {}

        # Build title page
        meta_lines = []
        if meta.get("version"):
            meta_lines.append(f"Version {meta['version']}")
        if meta.get("status"):
            meta_lines.append(f"Status: {meta['status'].title()}")
        if meta.get("document_number"):
            meta_lines.append(meta["document_number"])
        if meta.get("author"):
            meta_lines.append(f"Author: {meta['author']}")

        meta_html = "<br>".join(meta_lines) if meta_lines else ""

        title_page = f"""
        <div class="title-page">
            <h1>{title}</h1>
            {f'<div class="metadata">{meta_html}</div>' if meta_html else ''}
        </div>
        """

        # Build TOC page
        toc_html = ""
        if toc:
            toc_items = []
            for entry in toc:
                level = entry.get("level", 1)
                text = entry.get("text", "")
                anchor = entry.get("id", "")
                toc_items.append(
                    f'<li class="toc-level-{level}"><a href="#{anchor}">{text}</a></li>'
                )
            toc_html = f"""
            <div class="toc-page">
                <h2>Table of Contents</h2>
                <ul>{"".join(toc_items)}</ul>
            </div>
            """

        # Full document
        full_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>{PdfGenerator.PRINT_CSS}</style>
        </head>
        <body>
            {title_page}
            {toc_html}
            <div class="content">{content_html}</div>
        </body>
        </html>"""

        buf = io.BytesIO()
        HTML(string=full_html).write_pdf(buf)
        buf.seek(0)

        # Generate filename
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        filename = f"{slug}.pdf"

        return buf, filename
