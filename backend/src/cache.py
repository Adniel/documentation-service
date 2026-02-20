"""Redis cache service with graceful fallback."""

from __future__ import annotations

import functools
import hashlib
import json
import logging
from typing import Any, Callable

import redis.asyncio as aioredis

from src.config import get_settings

logger = logging.getLogger(__name__)

_cache_instance: RedisCache | None = None


class RedisCache:
    """Async Redis cache wrapper with graceful degradation."""

    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(key)
        except Exception:
            logger.warning("redis_get_failed", extra={"key": key})
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        try:
            await self._client.set(key, value, ex=ttl_seconds)
        except Exception:
            logger.warning("redis_set_failed", extra={"key": key})

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except Exception:
            logger.warning("redis_delete_failed", extra={"key": key})

    async def exists(self, key: str) -> bool:
        try:
            return bool(await self._client.exists(key))
        except Exception:
            logger.warning("redis_exists_failed", extra={"key": key})
            return False

    async def ping(self) -> bool:
        try:
            return await self._client.ping()
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()


async def init_cache() -> RedisCache:
    """Create and return a RedisCache instance."""
    global _cache_instance
    settings = get_settings()
    client = aioredis.from_url(settings.redis_url, decode_responses=True)
    _cache_instance = RedisCache(client)
    return _cache_instance


def get_cache() -> RedisCache | None:
    """Get the singleton cache instance (None if not initialized)."""
    return _cache_instance


def _build_cache_key(prefix: str, args: tuple, kwargs: dict) -> str:
    """Build a deterministic cache key from function arguments."""
    raw = json.dumps({"a": [str(a) for a in args], "k": {k: str(v) for k, v in sorted(kwargs.items())}}, sort_keys=True)
    digest = hashlib.md5(raw.encode()).hexdigest()  # noqa: S324
    return f"cache:{prefix}:{digest}"


def cached(ttl: int = 300, key_prefix: str | None = None) -> Callable:
    """Async decorator for caching function results in Redis.

    Args:
        ttl: Cache time-to-live in seconds.
        key_prefix: Custom key prefix (defaults to function qualified name).
    """

    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or func.__qualname__

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()
            if cache is None:
                return await func(*args, **kwargs)

            key = _build_cache_key(prefix, args, kwargs)

            hit = await cache.get(key)
            if hit is not None:
                try:
                    return json.loads(hit)
                except (json.JSONDecodeError, TypeError):
                    pass

            result = await func(*args, **kwargs)

            try:
                await cache.set(key, json.dumps(result), ttl_seconds=ttl)
            except (TypeError, ValueError):
                pass  # Non-serializable result, skip caching

            return result

        return wrapper

    return decorator
