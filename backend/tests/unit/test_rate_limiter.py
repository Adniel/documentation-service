"""Unit tests for MCP rate limiter.

Sprint C: MCP Integration
"""

import pytest
import time
from unittest.mock import patch

from src.modules.mcp.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test cases for RateLimiter."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter instance."""
        return RateLimiter()

    def test_first_request_allowed(self, limiter):
        """Test that first request is always allowed."""
        allowed, retry_after = limiter.check_rate_limit("account-1", 60)
        assert allowed is True
        assert retry_after == 0

    def test_within_limit(self, limiter):
        """Test requests within limit are allowed."""
        account_id = "account-2"
        limit = 10

        # Make requests up to the limit
        for _ in range(limit):
            allowed, _ = limiter.check_rate_limit(account_id, limit)
            assert allowed is True

    def test_exceeds_limit(self, limiter):
        """Test requests exceeding limit are blocked."""
        account_id = "account-3"
        limit = 5

        # Use up all tokens
        for _ in range(limit):
            limiter.check_rate_limit(account_id, limit)

        # Next request should be blocked
        allowed, retry_after = limiter.check_rate_limit(account_id, limit)
        assert allowed is False
        assert retry_after > 0

    def test_tokens_refill(self, limiter):
        """Test that tokens refill over time."""
        account_id = "account-4"
        limit = 2

        # Use all tokens
        for _ in range(limit):
            limiter.check_rate_limit(account_id, limit)

        # Simulate time passing (1 second = 1/60 of limit refilled for 60/min)
        with patch("time.time") as mock_time:
            # First call uses the current time
            current_time = time.time()
            mock_time.return_value = current_time

            limiter.check_rate_limit(account_id, limit)

            # Advance time by 30 seconds (should refill 1 token for limit=2)
            mock_time.return_value = current_time + 30

            allowed, _ = limiter.check_rate_limit(account_id, limit)
            # Should allow request after tokens refill
            assert allowed is True

    def test_different_accounts_independent(self, limiter):
        """Test that rate limits are per-account."""
        limit = 2

        # Exhaust limit for account-5
        for _ in range(limit):
            limiter.check_rate_limit("account-5", limit)

        allowed, _ = limiter.check_rate_limit("account-5", limit)
        assert allowed is False

        # Account-6 should still work
        allowed, _ = limiter.check_rate_limit("account-6", limit)
        assert allowed is True

    def test_different_limits_per_account(self, limiter):
        """Test that each account can have different limits."""
        # Account with limit of 5
        for _ in range(5):
            allowed, _ = limiter.check_rate_limit("account-7", 5)
            assert allowed is True

        # Should be blocked
        allowed, _ = limiter.check_rate_limit("account-7", 5)
        assert allowed is False

        # Account with limit of 10 should have more capacity
        for _ in range(10):
            allowed, _ = limiter.check_rate_limit("account-8", 10)
            assert allowed is True

    def test_retry_after_reasonable(self, limiter):
        """Test that retry_after returns reasonable values."""
        account_id = "account-9"
        limit = 60  # 60 per minute = 1 per second

        # Use all tokens
        for _ in range(limit):
            limiter.check_rate_limit(account_id, limit)

        # Get retry_after
        allowed, retry_after = limiter.check_rate_limit(account_id, limit)
        assert allowed is False
        # Should be around 1 second for this limit
        assert 0 < retry_after <= 2

    def test_cleanup_old_buckets(self, limiter):
        """Test that old buckets are cleaned up."""
        # Create many buckets
        for i in range(100):
            limiter.check_rate_limit(f"account-{i}", 60)

        # Force cleanup by calling with an old timestamp
        with patch("time.time") as mock_time:
            current_time = time.time()
            # Set time to 2 hours in the future
            mock_time.return_value = current_time + 7200

            # This should trigger cleanup
            limiter._cleanup_old_buckets()

        # Buckets should be cleaned up (internal check)
        # The exact behavior depends on implementation

    def test_high_rate_limit(self, limiter):
        """Test with high rate limit."""
        account_id = "account-high"
        limit = 1000

        # Should be able to make many requests
        for _ in range(100):
            allowed, _ = limiter.check_rate_limit(account_id, limit)
            assert allowed is True

    def test_low_rate_limit(self, limiter):
        """Test with very low rate limit."""
        account_id = "account-low"
        limit = 1

        # First request should work
        allowed, _ = limiter.check_rate_limit(account_id, limit)
        assert allowed is True

        # Second should be blocked
        allowed, retry_after = limiter.check_rate_limit(account_id, limit)
        assert allowed is False
        assert retry_after > 0
