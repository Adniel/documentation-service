"""API key authentication for MCP.

Sprint C: MCP Integration
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.db.models.service_account import ServiceAccount
from src.modules.mcp.rate_limiter import rate_limiter
from src.modules.mcp.service import ServiceAccountService


async def get_service_account(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> ServiceAccount:
    """Authenticate request using API key.

    Expected header format: Authorization: Bearer dsk_...

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <api_key>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = parts[1]
    if not api_key.startswith("dsk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    service = ServiceAccountService(db)
    account = await service.get_by_api_key(api_key)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service account is deactivated",
        )

    if service.is_expired(account):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service account has expired",
        )

    # Check IP allowlist
    client_ip = request.client.host if request.client else None
    if client_ip and not service.check_ip_allowed(account, client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IP address not allowed",
        )

    # Check rate limit
    allowed, retry_after = rate_limiter.check_rate_limit(
        account.id, account.rate_limit_per_minute
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    # Update last used
    account.last_used_at = datetime.now(timezone.utc)
    await db.flush()

    return account


# Type alias for dependency injection
McpServiceAccount = Annotated[ServiceAccount, Depends(get_service_account)]
