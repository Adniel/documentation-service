"""Rate limiting for MCP service accounts.

Sprint C: MCP Integration

Uses a token bucket algorithm for rate limiting. For production with
multiple workers, this should be replaced with a Redis-based implementation.
"""

import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RateLimitState:
    """State for a single rate limit window."""

    tokens: float = 0.0
    last_update: float = field(default_factory=time.time)


class RateLimiter:
    """Token bucket rate limiter for service accounts.

    Uses a simple in-memory implementation. For production with multiple
    workers, replace with Redis-based implementation.
    """

    def __init__(self):
        self._states: dict[str, RateLimitState] = {}
        self._lock = Lock()

    def _get_state(self, account_id: str) -> RateLimitState:
        """Get or create rate limit state for an account."""
        if account_id not in self._states:
            self._states[account_id] = RateLimitState()
        return self._states[account_id]

    def check_rate_limit(
        self,
        account_id: str,
        rate_limit_per_minute: int,
    ) -> tuple[bool, int]:
        """Check if request is allowed under rate limit.

        Args:
            account_id: Service account ID
            rate_limit_per_minute: Maximum requests per minute

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._lock:
            now = time.time()
            state = self._get_state(account_id)

            # Calculate tokens to add based on time elapsed
            elapsed = now - state.last_update
            tokens_to_add = elapsed * (rate_limit_per_minute / 60.0)

            # Update state
            state.tokens = min(rate_limit_per_minute, state.tokens + tokens_to_add)
            state.last_update = now

            if state.tokens >= 1:
                state.tokens -= 1
                return True, 0
            else:
                # Calculate retry after
                tokens_needed = 1 - state.tokens
                retry_after = int(tokens_needed * (60.0 / rate_limit_per_minute)) + 1
                return False, retry_after

    def reset(self, account_id: str) -> None:
        """Reset rate limit state for an account."""
        with self._lock:
            if account_id in self._states:
                del self._states[account_id]

    def get_remaining(self, account_id: str, rate_limit_per_minute: int) -> int:
        """Get remaining tokens for an account.

        Args:
            account_id: Service account ID
            rate_limit_per_minute: Maximum requests per minute

        Returns:
            Number of remaining requests allowed
        """
        with self._lock:
            now = time.time()
            state = self._get_state(account_id)

            # Calculate tokens to add based on time elapsed
            elapsed = now - state.last_update
            tokens_to_add = elapsed * (rate_limit_per_minute / 60.0)

            # Calculate current tokens (without modifying state)
            current_tokens = min(rate_limit_per_minute, state.tokens + tokens_to_add)
            return int(current_tokens)


# Global rate limiter instance
rate_limiter = RateLimiter()
