"""Service account management service.

Sprint C: MCP Integration
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.service_account import ServiceAccount, ServiceAccountUsage
from src.modules.mcp.schemas import (
    ServiceAccountCreate,
    ServiceAccountUpdate,
    UsageStatsResponse,
)


class ServiceAccountService:
    """Service for managing service accounts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_api_key() -> tuple[str, str, str]:
        """Generate a new API key.

        Returns:
            Tuple of (full_key, key_hash, key_prefix)
        """
        # Generate 32-byte random key, encode as hex (64 chars)
        key_bytes = secrets.token_bytes(32)
        full_key = f"dsk_{key_bytes.hex()}"  # dsk = doc service key
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        key_prefix = full_key[:12]  # "dsk_" + first 8 hex chars
        return full_key, key_hash, key_prefix

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def create(
        self,
        organization_id: str,
        created_by_id: str,
        data: ServiceAccountCreate,
    ) -> tuple[ServiceAccount, str]:
        """Create a new service account.

        Returns:
            Tuple of (service_account, api_key)
        """
        full_key, key_hash, key_prefix = self.generate_api_key()

        account = ServiceAccount(
            id=str(uuid4()),
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            api_key_hash=key_hash,
            api_key_prefix=key_prefix,
            role=data.role,
            allowed_spaces=data.allowed_spaces,
            allowed_operations=data.allowed_operations,
            ip_allowlist=data.ip_allowlist,
            rate_limit_per_minute=data.rate_limit_per_minute,
            expires_at=data.expires_at,
            created_by_id=created_by_id,
        )

        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)

        return account, full_key

    async def get_by_id(self, account_id: str) -> ServiceAccount | None:
        """Get service account by ID."""
        result = await self.db.execute(
            select(ServiceAccount)
            .where(ServiceAccount.id == account_id)
            .options(selectinload(ServiceAccount.created_by))
        )
        return result.scalar_one_or_none()

    async def get_by_api_key(self, api_key: str) -> ServiceAccount | None:
        """Get service account by API key."""
        key_hash = self.hash_api_key(api_key)
        key_prefix = api_key[:12]

        result = await self.db.execute(
            select(ServiceAccount).where(
                ServiceAccount.api_key_prefix == key_prefix,
                ServiceAccount.api_key_hash == key_hash,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: str,
        include_inactive: bool = False,
    ) -> list[ServiceAccount]:
        """List service accounts for an organization."""
        query = select(ServiceAccount).where(
            ServiceAccount.organization_id == organization_id
        )

        if not include_inactive:
            query = query.where(ServiceAccount.is_active == True)  # noqa: E712

        query = query.order_by(ServiceAccount.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        account: ServiceAccount,
        data: ServiceAccountUpdate,
    ) -> ServiceAccount:
        """Update a service account."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(account, field, value)

        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def rotate_api_key(
        self, account: ServiceAccount
    ) -> tuple[ServiceAccount, str]:
        """Rotate the API key for a service account."""
        full_key, key_hash, key_prefix = self.generate_api_key()

        account.api_key_hash = key_hash
        account.api_key_prefix = key_prefix

        await self.db.flush()
        await self.db.refresh(account)

        return account, full_key

    async def delete(self, account: ServiceAccount) -> None:
        """Delete a service account."""
        await self.db.delete(account)
        await self.db.flush()

    async def update_last_used(self, account: ServiceAccount) -> None:
        """Update the last_used_at timestamp."""
        account.last_used_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def record_usage(
        self,
        account_id: str,
        operation: str,
        response_code: int,
        ip_address: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        response_time_ms: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Record a usage event."""
        usage = ServiceAccountUsage(
            id=str(uuid4()),
            service_account_id=account_id,
            timestamp=datetime.now(timezone.utc),
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            response_code=response_code,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )
        self.db.add(usage)
        await self.db.flush()

    async def get_usage_stats(
        self,
        account_id: str,
        days: int = 30,
    ) -> UsageStatsResponse:
        """Get usage statistics for a service account."""
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=days)

        # Total counts
        total_result = await self.db.execute(
            select(
                func.count(ServiceAccountUsage.id).label("total"),
                func.count(ServiceAccountUsage.id)
                .filter(ServiceAccountUsage.response_code < 400)
                .label("successful"),
                func.avg(ServiceAccountUsage.response_time_ms).label("avg_time"),
            ).where(
                ServiceAccountUsage.service_account_id == account_id,
                ServiceAccountUsage.timestamp >= period_start,
            )
        )
        totals = total_result.one()

        # By operation
        op_result = await self.db.execute(
            select(
                ServiceAccountUsage.operation,
                func.count(ServiceAccountUsage.id).label("count"),
            )
            .where(
                ServiceAccountUsage.service_account_id == account_id,
                ServiceAccountUsage.timestamp >= period_start,
            )
            .group_by(ServiceAccountUsage.operation)
        )
        by_operation = {row.operation: row.count for row in op_result}

        # By day
        day_result = await self.db.execute(
            select(
                func.date_trunc("day", ServiceAccountUsage.timestamp).label("day"),
                func.count(ServiceAccountUsage.id).label("count"),
            )
            .where(
                ServiceAccountUsage.service_account_id == account_id,
                ServiceAccountUsage.timestamp >= period_start,
            )
            .group_by(func.date_trunc("day", ServiceAccountUsage.timestamp))
            .order_by(func.date_trunc("day", ServiceAccountUsage.timestamp))
        )
        by_day = [
            {"date": row.day.isoformat(), "count": row.count} for row in day_result
        ]

        return UsageStatsResponse(
            service_account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            total_requests=totals.total or 0,
            successful_requests=totals.successful or 0,
            failed_requests=(totals.total or 0) - (totals.successful or 0),
            avg_response_time_ms=float(totals.avg_time) if totals.avg_time else None,
            requests_by_operation=by_operation,
            requests_by_day=by_day,
        )

    def is_expired(self, account: ServiceAccount) -> bool:
        """Check if a service account has expired."""
        if account.expires_at is None:
            return False
        return datetime.now(timezone.utc) > account.expires_at

    def check_ip_allowed(self, account: ServiceAccount, ip_address: str) -> bool:
        """Check if an IP address is allowed."""
        import ipaddress as ipaddr

        if account.ip_allowlist is None:
            return True

        try:
            client_ip = ipaddr.ip_address(ip_address)
            for cidr in account.ip_allowlist:
                network = ipaddr.ip_network(cidr, strict=False)
                if client_ip in network:
                    return True
            return False
        except ValueError:
            return False
