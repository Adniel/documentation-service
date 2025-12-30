"""Sync service - Orchestrates Git remote synchronization.

Sprint 13: Git Remote Support

Provides:
- Push/pull orchestration based on sync strategy
- Conflict detection and handling
- Sync event logging
- Audit trail integration
"""

import json
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.organization import Organization
from src.db.models.git_sync_event import (
    GitSyncEvent,
    SyncEventType,
    SyncDirection,
    SyncStatus,
)
from src.modules.content.git_service import get_git_service
from src.modules.git.credential_service import CredentialService
from src.modules.audit.audit_service import AuditService


class SyncError(Exception):
    """Error during sync operation."""

    pass


class SyncService:
    """Service for orchestrating Git remote sync operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.git_service = get_git_service()
        self.credential_service = CredentialService(db)
        self.audit_service = AuditService(db)

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        result = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def _create_sync_event(
        self,
        org_id: str,
        event_type: SyncEventType,
        direction: SyncDirection,
        status: SyncStatus,
        branch: str,
        triggered_by_id: Optional[str] = None,
        trigger_source: Optional[str] = None,
        commit_sha_before: Optional[str] = None,
    ) -> GitSyncEvent:
        """Create a new sync event record."""
        event = GitSyncEvent(
            id=str(uuid4()),
            organization_id=org_id,
            event_type=event_type,
            direction=direction,
            status=status,
            branch_name=branch,
            triggered_by_id=triggered_by_id,
            trigger_source=trigger_source,
            commit_sha_before=commit_sha_before,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def _update_sync_event(
        self,
        event: GitSyncEvent,
        status: SyncStatus,
        commit_sha_after: Optional[str] = None,
        error_message: Optional[str] = None,
        files_changed: Optional[list[str]] = None,
    ) -> GitSyncEvent:
        """Update sync event with results."""
        event.status = status
        event.completed_at = datetime.now(timezone.utc)
        if commit_sha_after:
            event.commit_sha_after = commit_sha_after
        if error_message:
            event.error_message = error_message
        if files_changed:
            event.files_changed = json.dumps(files_changed)
        await self.db.flush()
        return event

    async def _update_org_sync_status(
        self,
        org: Organization,
        status: str,
        last_sync: Optional[datetime] = None,
    ) -> None:
        """Update organization sync status."""
        org.git_sync_status = status
        if last_sync:
            org.git_last_sync_at = last_sync
        await self.db.flush()

    async def push_sync(
        self,
        org_id: str,
        branch: Optional[str] = None,
        triggered_by_id: Optional[str] = None,
        trigger_source: str = "manual",
        force: bool = False,
    ) -> dict:
        """Push local changes to remote.

        Args:
            org_id: Organization ID
            branch: Branch to push (uses default if not specified)
            triggered_by_id: User who triggered sync
            trigger_source: Source of trigger (manual, page_save, webhook)
            force: Force push

        Returns:
            Dict with sync results
        """
        org = await self.get_organization(org_id)
        if not org:
            raise SyncError("Organization not found")

        if not org.git_remote_url:
            raise SyncError("No remote configured for this organization")

        if not org.git_sync_enabled:
            raise SyncError("Sync is disabled for this organization")

        branch = branch or org.git_default_branch

        # Get credential
        credential_value = await self.credential_service.get_decrypted_credential(org_id)
        if not credential_value:
            raise SyncError("No credentials configured for remote access")

        credential = await self.credential_service.get_credential(org_id)
        credential_type = credential.credential_type.value if credential else "https_token"

        # Get current commit SHA
        commit_sha_before = self.git_service.get_head_sha(org.slug)

        # Create sync event
        event = await self._create_sync_event(
            org_id=org_id,
            event_type=SyncEventType.PUSH,
            direction=SyncDirection.OUTBOUND,
            status=SyncStatus.IN_PROGRESS,
            branch=branch,
            triggered_by_id=triggered_by_id,
            trigger_source=trigger_source,
            commit_sha_before=commit_sha_before,
        )

        # Update org status
        await self._update_org_sync_status(org, "pending")

        try:
            # Ensure remote is configured in Git
            self.git_service.add_remote(org.slug, org.git_remote_url)

            # Push
            result = self.git_service.push_to_remote(
                org_slug=org.slug,
                branch=branch,
                credential=credential_value,
                credential_type=credential_type,
                force=force,
            )

            if result.get("success"):
                await self._update_sync_event(
                    event,
                    status=SyncStatus.SUCCESS,
                    commit_sha_after=result.get("commit_sha"),
                )
                await self._update_org_sync_status(
                    org,
                    status="synced",
                    last_sync=datetime.now(timezone.utc),
                )

                # Audit log
                await self.audit_service.log_event(
                    event_type="git.sync_completed",
                    actor_id=triggered_by_id,
                    resource_type="organization",
                    resource_id=org_id,
                    details={
                        "sync_type": "push",
                        "branch": branch,
                        "commit_sha": result.get("commit_sha"),
                    },
                )

                return {
                    "success": True,
                    "event_id": event.id,
                    "event_type": "push",
                    "status": "success",
                    "branch": branch,
                    "commit_sha_before": commit_sha_before,
                    "commit_sha_after": result.get("commit_sha"),
                }
            else:
                error_msg = result.get("error", "Unknown push error")
                await self._update_sync_event(
                    event,
                    status=SyncStatus.FAILED,
                    error_message=error_msg,
                )
                await self._update_org_sync_status(org, status="error")

                # Audit log
                await self.audit_service.log_event(
                    event_type="git.sync_failed",
                    actor_id=triggered_by_id,
                    resource_type="organization",
                    resource_id=org_id,
                    details={
                        "sync_type": "push",
                        "branch": branch,
                        "error": error_msg,
                    },
                )

                return {
                    "success": False,
                    "event_id": event.id,
                    "event_type": "push",
                    "status": "failed",
                    "branch": branch,
                    "message": error_msg,
                }

        except Exception as e:
            await self._update_sync_event(
                event,
                status=SyncStatus.FAILED,
                error_message=str(e),
            )
            await self._update_org_sync_status(org, status="error")
            raise SyncError(f"Push sync failed: {e}")

    async def pull_sync(
        self,
        org_id: str,
        branch: Optional[str] = None,
        triggered_by_id: Optional[str] = None,
        trigger_source: str = "manual",
    ) -> dict:
        """Pull changes from remote.

        Args:
            org_id: Organization ID
            branch: Branch to pull (uses default if not specified)
            triggered_by_id: User who triggered sync
            trigger_source: Source of trigger

        Returns:
            Dict with sync results
        """
        org = await self.get_organization(org_id)
        if not org:
            raise SyncError("Organization not found")

        if not org.git_remote_url:
            raise SyncError("No remote configured for this organization")

        if not org.git_sync_enabled:
            raise SyncError("Sync is disabled for this organization")

        branch = branch or org.git_default_branch

        # Get credential
        credential_value = await self.credential_service.get_decrypted_credential(org_id)
        if not credential_value:
            raise SyncError("No credentials configured for remote access")

        credential = await self.credential_service.get_credential(org_id)
        credential_type = credential.credential_type.value if credential else "https_token"

        # Get current commit SHA
        commit_sha_before = self.git_service.get_head_sha(org.slug)

        # Create sync event
        event = await self._create_sync_event(
            org_id=org_id,
            event_type=SyncEventType.PULL,
            direction=SyncDirection.INBOUND,
            status=SyncStatus.IN_PROGRESS,
            branch=branch,
            triggered_by_id=triggered_by_id,
            trigger_source=trigger_source,
            commit_sha_before=commit_sha_before,
        )

        # Update org status
        await self._update_org_sync_status(org, "pending")

        try:
            # Ensure remote is configured in Git
            self.git_service.add_remote(org.slug, org.git_remote_url)

            # Pull
            result = self.git_service.pull_from_remote(
                org_slug=org.slug,
                branch=branch,
                credential=credential_value,
                credential_type=credential_type,
            )

            if result.get("success"):
                status = SyncStatus.SUCCESS
                if result.get("updated"):
                    commit_sha_after = result.get("commit_sha")
                else:
                    commit_sha_after = commit_sha_before

                await self._update_sync_event(
                    event,
                    status=status,
                    commit_sha_after=commit_sha_after,
                )
                await self._update_org_sync_status(
                    org,
                    status="synced",
                    last_sync=datetime.now(timezone.utc),
                )

                # Audit log
                await self.audit_service.log_event(
                    event_type="git.sync_completed",
                    actor_id=triggered_by_id,
                    resource_type="organization",
                    resource_id=org_id,
                    details={
                        "sync_type": "pull",
                        "branch": branch,
                        "updated": result.get("updated", False),
                        "commit_sha": commit_sha_after,
                    },
                )

                return {
                    "success": True,
                    "event_id": event.id,
                    "event_type": "pull",
                    "status": "success",
                    "branch": branch,
                    "commit_sha_before": commit_sha_before,
                    "commit_sha_after": commit_sha_after,
                    "updated": result.get("updated", False),
                    "message": result.get("message", ""),
                }
            else:
                error_msg = result.get("error", "Unknown pull error")
                conflict_files = result.get("conflict_files", [])

                if conflict_files:
                    status = SyncStatus.CONFLICT
                    await self._update_org_sync_status(org, status="conflict")
                else:
                    status = SyncStatus.FAILED
                    await self._update_org_sync_status(org, status="error")

                await self._update_sync_event(
                    event,
                    status=status,
                    error_message=error_msg,
                    files_changed=conflict_files,
                )

                # Audit log
                await self.audit_service.log_event(
                    event_type="git.sync_failed" if not conflict_files else "git.sync_conflict",
                    actor_id=triggered_by_id,
                    resource_type="organization",
                    resource_id=org_id,
                    details={
                        "sync_type": "pull",
                        "branch": branch,
                        "error": error_msg,
                        "conflict_files": conflict_files,
                    },
                )

                return {
                    "success": False,
                    "event_id": event.id,
                    "event_type": "pull",
                    "status": "conflict" if conflict_files else "failed",
                    "branch": branch,
                    "message": error_msg,
                    "files_changed": conflict_files,
                }

        except Exception as e:
            await self._update_sync_event(
                event,
                status=SyncStatus.FAILED,
                error_message=str(e),
            )
            await self._update_org_sync_status(org, status="error")
            raise SyncError(f"Pull sync failed: {e}")

    async def sync(
        self,
        org_id: str,
        branch: Optional[str] = None,
        triggered_by_id: Optional[str] = None,
        trigger_source: str = "manual",
        force: bool = False,
    ) -> dict:
        """Sync based on organization's sync strategy.

        Args:
            org_id: Organization ID
            branch: Branch to sync
            triggered_by_id: User who triggered sync
            trigger_source: Source of trigger
            force: Force sync operations

        Returns:
            Dict with sync results
        """
        org = await self.get_organization(org_id)
        if not org:
            raise SyncError("Organization not found")

        strategy = org.git_sync_strategy or "push_only"

        if strategy == "push_only":
            return await self.push_sync(
                org_id, branch, triggered_by_id, trigger_source, force
            )
        elif strategy == "pull_only":
            return await self.pull_sync(
                org_id, branch, triggered_by_id, trigger_source
            )
        elif strategy == "bidirectional":
            # For bidirectional, pull first then push
            pull_result = await self.pull_sync(
                org_id, branch, triggered_by_id, trigger_source
            )
            if not pull_result.get("success"):
                return pull_result

            # Only push if pull succeeded
            return await self.push_sync(
                org_id, branch, triggered_by_id, trigger_source, force
            )
        else:
            raise SyncError(f"Unknown sync strategy: {strategy}")

    async def get_sync_status(self, org_id: str) -> dict:
        """Get current sync status for organization.

        Args:
            org_id: Organization ID

        Returns:
            Dict with sync status info
        """
        org = await self.get_organization(org_id)
        if not org:
            raise SyncError("Organization not found")

        branch = org.git_default_branch

        # Check divergence if remote is configured
        divergence = {}
        if org.git_remote_url:
            divergence = self.git_service.get_divergence(org.slug, branch)

        return {
            "organization_id": org_id,
            "sync_enabled": org.git_sync_enabled,
            "sync_strategy": org.git_sync_strategy,
            "sync_status": org.git_sync_status or "not_configured",
            "last_sync_at": org.git_last_sync_at.isoformat() if org.git_last_sync_at else None,
            "default_branch": branch,
            "remote_url": org.git_remote_url,
            "provider": org.git_remote_provider,
            "divergence": divergence,
        }

    async def get_sync_history(
        self,
        org_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """Get sync history for organization.

        Args:
            org_id: Organization ID
            limit: Max events to return
            offset: Offset for pagination

        Returns:
            Dict with events list and total count
        """
        # Count total
        from sqlalchemy import func

        count_result = await self.db.execute(
            select(func.count(GitSyncEvent.id)).where(
                GitSyncEvent.organization_id == org_id
            )
        )
        total = count_result.scalar() or 0

        # Get events
        result = await self.db.execute(
            select(GitSyncEvent)
            .where(GitSyncEvent.organization_id == org_id)
            .order_by(desc(GitSyncEvent.created_at))
            .limit(limit)
            .offset(offset)
        )
        events = result.scalars().all()

        return {
            "events": [
                {
                    "id": str(e.id),
                    "event_type": e.event_type.value,
                    "direction": e.direction.value,
                    "status": e.status.value,
                    "branch_name": e.branch_name,
                    "commit_sha_before": e.commit_sha_before,
                    "commit_sha_after": e.commit_sha_after,
                    "error_message": e.error_message,
                    "trigger_source": e.trigger_source,
                    "triggered_by_id": e.triggered_by_id,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                    "started_at": e.started_at.isoformat() if e.started_at else None,
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                    "duration_seconds": e.duration_seconds,
                }
                for e in events
            ],
            "total": total,
        }

    async def test_connection(self, org_id: str) -> dict:
        """Test connection to remote repository.

        Args:
            org_id: Organization ID

        Returns:
            Dict with connection test results
        """
        org = await self.get_organization(org_id)
        if not org:
            return {"success": False, "message": "Organization not found"}

        if not org.git_remote_url:
            return {"success": False, "message": "No remote URL configured"}

        # Get credential
        credential_value = await self.credential_service.get_decrypted_credential(org_id)
        if not credential_value:
            return {"success": False, "message": "No credentials configured"}

        credential = await self.credential_service.get_credential(org_id)
        credential_type = credential.credential_type.value if credential else "https_token"

        try:
            # Ensure remote is configured
            self.git_service.add_remote(org.slug, org.git_remote_url)

            # Try to fetch
            result = self.git_service.fetch_remote(
                org_slug=org.slug,
                credential=credential_value,
                credential_type=credential_type,
            )

            if result.get("success"):
                return {
                    "success": True,
                    "message": "Connection successful",
                    "remote_url": org.git_remote_url,
                    "default_branch": org.git_default_branch,
                }
            else:
                return {
                    "success": False,
                    "message": result.get("error", "Connection failed"),
                }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
            }
