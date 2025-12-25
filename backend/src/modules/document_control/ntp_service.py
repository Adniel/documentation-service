"""NTP Timestamp Service for 21 CFR Part 11 compliance.

Provides trusted timestamps from NTP servers for electronic signatures.
Timestamps are required for signature manifestation per §11.50.

This service:
- Queries multiple NTP servers with failover
- Returns both the timestamp and the source server for audit
- Handles network failures gracefully with fallback
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Tuple

import ntplib

logger = logging.getLogger(__name__)


# NTP servers in priority order
# Using well-known, reliable NTP servers
NTP_SERVERS = [
    "pool.ntp.org",
    "time.google.com",
    "time.windows.com",
    "time.apple.com",
    "time.cloudflare.com",
]

# Timeout for NTP queries (seconds)
NTP_TIMEOUT = 3

# Maximum allowed drift from local time (seconds)
# If NTP time differs by more than this, log a warning
MAX_ALLOWED_DRIFT_SECONDS = 60


class NTPServiceError(Exception):
    """Raised when NTP timestamp cannot be obtained."""
    pass


class NTPService:
    """Service for obtaining trusted timestamps from NTP servers."""

    def __init__(self, servers: list[str] | None = None, timeout: float = NTP_TIMEOUT):
        """Initialize NTP service.

        Args:
            servers: List of NTP servers to query (uses defaults if None)
            timeout: Timeout for each NTP query in seconds
        """
        self.servers = servers or NTP_SERVERS
        self.timeout = timeout
        self._client = ntplib.NTPClient()

    def _query_server_sync(self, server: str) -> Tuple[datetime, str]:
        """Query a single NTP server synchronously.

        Args:
            server: NTP server hostname

        Returns:
            Tuple of (timestamp, server_name)

        Raises:
            ntplib.NTPException: If query fails
        """
        response = self._client.request(server, version=3, timeout=self.timeout)
        # Convert NTP timestamp to datetime
        timestamp = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
        return timestamp, server

    async def get_trusted_timestamp(self) -> Tuple[datetime, str]:
        """Get a trusted timestamp from an NTP server.

        Tries servers in order until one succeeds. Returns the timestamp
        and the name of the server that provided it (for audit trail).

        Returns:
            Tuple of (timestamp, server_name)

        Raises:
            NTPServiceError: If no NTP servers could be reached
        """
        errors = []

        for server in self.servers:
            try:
                # Run NTP query in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                timestamp, used_server = await loop.run_in_executor(
                    None, self._query_server_sync, server
                )

                # Check for excessive drift from local time
                local_now = datetime.now(tz=timezone.utc)
                drift = abs((timestamp - local_now).total_seconds())
                if drift > MAX_ALLOWED_DRIFT_SECONDS:
                    logger.warning(
                        f"NTP time from {server} differs from local by {drift:.1f}s. "
                        f"NTP: {timestamp}, Local: {local_now}"
                    )

                logger.debug(f"Got NTP timestamp from {server}: {timestamp}")
                return timestamp, used_server

            except ntplib.NTPException as e:
                errors.append(f"{server}: {e}")
                logger.warning(f"NTP query to {server} failed: {e}")
                continue
            except OSError as e:
                errors.append(f"{server}: {e}")
                logger.warning(f"Network error querying {server}: {e}")
                continue
            except Exception as e:
                errors.append(f"{server}: {e}")
                logger.error(f"Unexpected error querying {server}: {e}")
                continue

        # All servers failed
        error_details = "; ".join(errors)
        raise NTPServiceError(
            f"Failed to obtain NTP timestamp from any server. Errors: {error_details}"
        )

    async def get_timestamp_with_fallback(self) -> Tuple[datetime, str]:
        """Get timestamp with fallback to local time if NTP fails.

        This should only be used in development/testing. Production
        systems should fail if NTP is unavailable.

        Returns:
            Tuple of (timestamp, source)
        """
        try:
            return await self.get_trusted_timestamp()
        except NTPServiceError:
            logger.error(
                "NTP service unavailable, falling back to local time. "
                "This should not happen in production!"
            )
            return datetime.now(tz=timezone.utc), "local_fallback"


# Global service instance
_ntp_service: NTPService | None = None


def get_ntp_service() -> NTPService:
    """Get the global NTP service instance."""
    global _ntp_service
    if _ntp_service is None:
        _ntp_service = NTPService()
    return _ntp_service


async def get_trusted_timestamp() -> Tuple[datetime, str]:
    """Convenience function to get a trusted timestamp.

    Returns:
        Tuple of (timestamp, server_name)

    Raises:
        NTPServiceError: If no NTP servers could be reached
    """
    service = get_ntp_service()
    return await service.get_trusted_timestamp()
