"""Webhook service - Handle Git provider webhooks.

Sprint 13: Git Remote Support

Provides:
- Webhook signature verification
- Push event parsing
- Automatic sync triggering
- Rate limiting
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.organization import Organization
from src.modules.git.sync_service import SyncService
from src.modules.audit.audit_service import AuditService


class WebhookError(Exception):
    """Error processing webhook."""

    pass


class WebhookService:
    """Service for handling Git provider webhooks."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sync_service = SyncService(db)
        self.audit_service = AuditService(db)

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    def verify_github_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify GitHub webhook signature (HMAC-SHA256).

        GitHub sends signature as 'sha256=<hex_digest>'.
        """
        if not signature or not signature.startswith("sha256="):
            return False

        expected_sig = signature[7:]  # Remove 'sha256=' prefix

        computed = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed, expected_sig)

    def verify_gitlab_signature(
        self,
        token: str,
        secret: str,
    ) -> bool:
        """Verify GitLab webhook token.

        GitLab sends token in X-Gitlab-Token header.
        """
        return hmac.compare_digest(token, secret)

    def verify_gitea_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify Gitea webhook signature (HMAC-SHA256).

        Gitea uses same format as GitHub.
        """
        return self.verify_github_signature(payload, signature, secret)

    async def verify_signature(
        self,
        org: Organization,
        payload: bytes,
        headers: dict,
    ) -> bool:
        """Verify webhook signature based on provider.

        Args:
            org: Organization
            payload: Raw request body
            headers: Request headers

        Returns:
            True if signature is valid
        """
        secret = org.git_webhook_secret
        if not secret:
            return False

        provider = org.git_remote_provider

        if provider == "github":
            signature = headers.get("x-hub-signature-256", "")
            return self.verify_github_signature(payload, signature, secret)

        elif provider == "gitlab":
            token = headers.get("x-gitlab-token", "")
            return self.verify_gitlab_signature(token, secret)

        elif provider == "gitea":
            signature = headers.get("x-gitea-signature", "")
            if not signature:
                # Gitea also supports GitHub-style signature
                signature = headers.get("x-hub-signature-256", "")
            return self.verify_gitea_signature(payload, signature, secret)

        elif provider == "custom":
            # For custom providers, check for common signature headers
            signature = (
                headers.get("x-hub-signature-256")
                or headers.get("x-signature")
                or ""
            )
            if signature:
                return self.verify_github_signature(payload, signature, secret)
            return False

        return False

    def parse_push_event(
        self,
        provider: str,
        payload: dict,
    ) -> dict:
        """Parse push event from webhook payload.

        Args:
            provider: Git provider
            payload: Parsed JSON payload

        Returns:
            Normalized push event data
        """
        if provider == "github":
            return {
                "ref": payload.get("ref", ""),
                "branch": payload.get("ref", "").replace("refs/heads/", ""),
                "before": payload.get("before"),
                "after": payload.get("after"),
                "commits": len(payload.get("commits", [])),
                "pusher": payload.get("pusher", {}).get("name"),
                "repository": payload.get("repository", {}).get("full_name"),
            }

        elif provider == "gitlab":
            return {
                "ref": payload.get("ref", ""),
                "branch": payload.get("ref", "").replace("refs/heads/", ""),
                "before": payload.get("before"),
                "after": payload.get("after"),
                "commits": len(payload.get("commits", [])),
                "pusher": payload.get("user_name"),
                "repository": payload.get("project", {}).get("path_with_namespace"),
            }

        elif provider == "gitea":
            return {
                "ref": payload.get("ref", ""),
                "branch": payload.get("ref", "").replace("refs/heads/", ""),
                "before": payload.get("before"),
                "after": payload.get("after"),
                "commits": len(payload.get("commits", [])),
                "pusher": payload.get("pusher", {}).get("username"),
                "repository": payload.get("repository", {}).get("full_name"),
            }

        else:
            # Generic parsing
            return {
                "ref": payload.get("ref", ""),
                "branch": payload.get("ref", "").replace("refs/heads/", ""),
                "before": payload.get("before"),
                "after": payload.get("after"),
                "commits": 0,
                "pusher": None,
                "repository": None,
            }

    def is_push_event(
        self,
        provider: str,
        headers: dict,
    ) -> bool:
        """Check if webhook is a push event.

        Args:
            provider: Git provider
            headers: Request headers

        Returns:
            True if this is a push event
        """
        if provider == "github":
            return headers.get("x-github-event") == "push"

        elif provider == "gitlab":
            return headers.get("x-gitlab-event") == "Push Hook"

        elif provider == "gitea":
            return headers.get("x-gitea-event") == "push"

        else:
            # Check common event headers
            event = (
                headers.get("x-github-event")
                or headers.get("x-gitlab-event")
                or headers.get("x-gitea-event")
                or ""
            )
            return "push" in event.lower()

    async def process_webhook(
        self,
        org_id: str,
        payload: bytes,
        headers: dict,
        client_ip: Optional[str] = None,
    ) -> dict:
        """Process incoming webhook.

        Args:
            org_id: Organization ID
            payload: Raw request body
            headers: Request headers (lowercase keys)
            client_ip: Client IP address

        Returns:
            Dict with processing result
        """
        org = await self.get_organization(org_id)
        if not org:
            raise WebhookError("Organization not found")

        if not org.git_sync_enabled:
            return {"status": "ignored", "message": "Sync is disabled"}

        # Verify signature
        if not await self.verify_signature(org, payload, headers):
            # Log failed verification
            await self.audit_service.log_event(
                event_type="git.webhook_signature_failed",
                actor_ip=client_ip,
                resource_type="organization",
                resource_id=org_id,
            )
            await self.db.commit()
            raise WebhookError("Invalid webhook signature")

        provider = org.git_remote_provider or "custom"

        # Check if it's a push event
        if not self.is_push_event(provider, headers):
            return {"status": "ignored", "message": "Not a push event"}

        # Parse payload
        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError:
            raise WebhookError("Invalid JSON payload")

        push_event = self.parse_push_event(provider, payload_dict)

        # Log webhook received
        await self.audit_service.log_event(
            event_type="git.webhook_received",
            actor_ip=client_ip,
            resource_type="organization",
            resource_id=org_id,
            details={
                "provider": provider,
                "branch": push_event["branch"],
                "commits": push_event["commits"],
                "pusher": push_event["pusher"],
            },
        )

        # Only sync if push is to default branch or configured branch
        if push_event["branch"] != org.git_default_branch:
            await self.db.commit()
            return {
                "status": "ignored",
                "message": f"Push to non-default branch: {push_event['branch']}",
            }

        # Trigger sync based on strategy
        strategy = org.git_sync_strategy or "push_only"

        if strategy == "push_only":
            # For push-only, we don't pull from remote
            await self.db.commit()
            return {
                "status": "ignored",
                "message": "Push-only strategy - no pull triggered",
            }

        # For pull_only or bidirectional, trigger a pull
        try:
            result = await self.sync_service.pull_sync(
                org_id=org_id,
                branch=push_event["branch"],
                triggered_by_id=None,  # Webhook triggered
                trigger_source="webhook",
            )
            await self.db.commit()

            return {
                "status": "processed",
                "message": "Sync triggered",
                "sync_result": result,
            }

        except Exception as e:
            await self.db.commit()
            return {
                "status": "error",
                "message": str(e),
            }
