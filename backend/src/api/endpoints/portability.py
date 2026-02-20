"""Portability API endpoints for export/import.

Sprint G: Metadata Portability
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from src.api.deps import DbSession, CurrentUser
from src.modules.portability.exporter import ExportService
from src.modules.portability.importer import ImportService
from src.modules.portability.schemas import (
    ExportScope,
    ImportExecuteRequest,
    ImportPreviewResponse,
    ImportResult,
)

router = APIRouter()

# Temporary directory for import uploads (cleaned up after use)
_IMPORT_TEMP_BASE = Path(tempfile.gettempdir()) / "docservice_imports"


# ============================================================================
# Export endpoints
# ============================================================================


@router.post("/export")
async def export_content(
    db: DbSession,
    current_user: CurrentUser,
    scope: ExportScope = Query(..., description="Export scope"),
    resource_id: str = Query(..., description="ID of resource to export"),
    include_content: bool = Query(True, description="Include page content"),
) -> StreamingResponse:
    """Export content to a ZIP archive.

    Supports exporting at organization, workspace, or space level.
    Returns a streaming ZIP download.
    """
    export_service = ExportService(db)

    try:
        if scope == ExportScope.ORGANIZATION:
            buf, filename, stats = await export_service.export_organization(
                resource_id, current_user.email, include_content
            )
        elif scope == ExportScope.WORKSPACE:
            buf, filename, stats = await export_service.export_workspace(
                resource_id, current_user.email, include_content
            )
        elif scope == ExportScope.SPACE:
            buf, filename, stats = await export_service.export_space(
                resource_id, current_user.email, include_content
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export scope: {scope}",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Export-Workspaces": str(stats.get("workspaces", 0)),
            "X-Export-Spaces": str(stats.get("spaces", 0)),
            "X-Export-Pages": str(stats.get("pages", 0)),
        },
    )


# ============================================================================
# Import endpoints
# ============================================================================


@router.post("/import/upload", response_model=dict)
async def upload_import(
    current_user: CurrentUser,
    file: UploadFile = File(..., description="ZIP archive or file to import"),
) -> dict:
    """Upload a file for import.

    Accepts ZIP archives (docservice exports, Confluence exports)
    or individual files. Returns a session_id for subsequent
    preview/execute calls.
    """
    _IMPORT_TEMP_BASE.mkdir(parents=True, exist_ok=True)

    # Create a unique import session directory
    import uuid
    session_id = str(uuid.uuid4())
    session_dir = _IMPORT_TEMP_BASE / session_id
    session_dir.mkdir()

    try:
        # Save uploaded file
        upload_path = session_dir / (file.filename or "upload.zip")
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract if ZIP
        extract_dir = session_dir / "extracted"
        extract_dir.mkdir()

        if file.filename and file.filename.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(upload_path, "r") as zf:
                zf.extractall(extract_dir)
        else:
            # Copy single file to extracted dir
            shutil.copy2(upload_path, extract_dir / upload_path.name)

        return {
            "session_id": session_id,
            "filename": file.filename,
            "size_bytes": len(content),
        }
    except Exception as e:
        # Clean up on error
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process upload: {str(e)}",
        )


@router.post("/import/preview", response_model=ImportPreviewResponse)
async def preview_import(
    db: DbSession,
    current_user: CurrentUser,
    session_id: str = Query(..., description="Import session ID from upload"),
    target_workspace_id: str = Query(..., description="Target workspace ID"),
    target_space_id: str | None = Query(None, description="Target space ID"),
) -> ImportPreviewResponse:
    """Preview what an import will do.

    Analyzes the uploaded content and returns a list of items
    that would be created, updated, or conflict with existing content.
    """
    extract_dir = _IMPORT_TEMP_BASE / session_id / "extracted"
    if not extract_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import session not found. Upload a file first.",
        )

    import_service = ImportService(db)
    return await import_service.preview(extract_dir, target_workspace_id, target_space_id)


@router.post("/import/execute", response_model=ImportResult)
async def execute_import(
    request: ImportExecuteRequest,
    db: DbSession,
    current_user: CurrentUser,
    session_id: str = Query(..., description="Import session ID from upload"),
) -> ImportResult:
    """Execute an import after reviewing the preview.

    Creates pages in the target workspace/space based on the
    uploaded content and conflict resolution settings.
    """
    session_dir = _IMPORT_TEMP_BASE / session_id
    extract_dir = session_dir / "extracted"
    if not extract_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import session not found. Upload a file first.",
        )

    import_service = ImportService(db)
    try:
        result = await import_service.execute(
            extract_dir, request, author_id=str(current_user.id)
        )
    finally:
        # Clean up temp files after execution
        shutil.rmtree(session_dir, ignore_errors=True)

    return result


@router.delete("/import/{session_id}")
async def cancel_import(
    session_id: str,
    current_user: CurrentUser,
) -> dict:
    """Cancel an import and clean up temporary files."""
    session_dir = _IMPORT_TEMP_BASE / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
    return {"status": "cancelled"}
