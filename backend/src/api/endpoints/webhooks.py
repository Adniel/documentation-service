"""Webhook API endpoints.

Sprint 13: Git Remote Support

Handles incoming webhooks from Git providers (GitHub, GitLab, Gitea).
"""

from fastapi import APIRouter, HTTPException, Request, status

from src.api.deps import DbSession
from src.modules.git.webhook_service import WebhookService, WebhookError

router = APIRouter()


@router.post("/git/{org_id}")
async def receive_git_webhook(
    org_id: str,
    request: Request,
    db: DbSession,
) -> dict:
    """Receive webhook from Git provider.

    This endpoint is called by GitHub, GitLab, Gitea when pushes occur.
    Verifies signature and triggers sync if configured.
    """
    # Get raw body
    body = await request.body()

    # Normalize headers to lowercase
    headers = {k.lower(): v for k, v in request.headers.items()}

    # Get client IP
    client_ip = request.client.host if request.client else None

    webhook_service = WebhookService(db)

    try:
        result = await webhook_service.process_webhook(
            org_id=org_id,
            payload=body,
            headers=headers,
            client_ip=client_ip,
        )
        return result
    except WebhookError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
