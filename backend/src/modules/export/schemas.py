"""Schemas for the export module.

Sprint I: Reader UI & Accessibility
"""

from enum import Enum

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats."""

    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    HTML = "html"


class ExportRequest(BaseModel):
    """Request to export one or more pages."""

    page_ids: list[str] = Field(..., min_length=1, max_length=50)
    format: ExportFormat = ExportFormat.PDF


class RenderResponse(BaseModel):
    """Response for page render endpoint."""

    content_html: str
    toc: list[dict]
    title: str

    class Config:
        from_attributes = True
