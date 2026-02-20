"""Export API endpoints for PDF, DOCX, and Markdown generation.

Sprint I: Reader UI & Accessibility
"""

import io
import zipfile
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from src.api.deps import DbSession, CurrentUser
from src.modules.content.service import get_page
from src.modules.publishing.renderer import render_page_content
from src.modules.export.pdf_generator import PdfGenerator
from src.modules.export.docx_generator import DocxGenerator
from src.modules.export.markdown_exporter import MarkdownExporter
from src.modules.export.schemas import ExportRequest, ExportFormat

router = APIRouter()


def _build_metadata(page: Any) -> dict[str, Any]:
    """Extract metadata from a page for export."""
    return {
        "version": page.version,
        "status": page.status,
        "document_number": getattr(page, "document_number", None),
        "author": getattr(page, "author_id", None),
        "diataxis_types": getattr(page, "diataxis_types", []),
        "summary": getattr(page, "summary", None),
    }


@router.get("/pages/{page_id}/pdf")
async def export_page_pdf(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """Export a page as PDF."""
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    content = page.content or {"type": "doc", "content": []}
    content_html, toc = render_page_content(content)
    metadata = _build_metadata(page)

    buf, filename = PdfGenerator.generate(content_html, page.title, toc, metadata)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/pages/{page_id}/docx")
async def export_page_docx(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """Export a page as DOCX."""
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    content = page.content or {"type": "doc", "content": []}
    _, toc = render_page_content(content)
    metadata = _build_metadata(page)

    buf, filename = DocxGenerator.generate(content, page.title, toc, metadata)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/pages/{page_id}/markdown")
async def export_page_markdown(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """Export a page as Markdown with YAML frontmatter."""
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    content = page.content or {"type": "doc", "content": []}
    metadata = _build_metadata(page)

    buf, filename = MarkdownExporter.generate(content, page.title, metadata)

    return StreamingResponse(
        buf,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/batch")
async def export_batch(
    request: ExportRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """Export multiple pages as a ZIP archive.

    Accepts page IDs and a format, generates each document,
    and returns them bundled in a ZIP file.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for page_id in request.page_ids:
            page = await get_page(db, page_id)
            if not page or not page.is_active:
                continue

            content = page.content or {"type": "doc", "content": []}
            content_html, toc = render_page_content(content)
            metadata = _build_metadata(page)

            if request.format == ExportFormat.PDF:
                file_buf, filename = PdfGenerator.generate(
                    content_html, page.title, toc, metadata
                )
            elif request.format == ExportFormat.DOCX:
                file_buf, filename = DocxGenerator.generate(
                    content, page.title, toc, metadata
                )
            elif request.format == ExportFormat.MARKDOWN:
                file_buf, filename = MarkdownExporter.generate(
                    content, page.title, metadata
                )
            else:
                # HTML export
                file_buf = io.BytesIO(content_html.encode("utf-8"))
                slug = page.slug or "page"
                filename = f"{slug}.html"

            zf.writestr(filename, file_buf.getvalue())

    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="export.zip"'},
    )
