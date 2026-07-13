"""Cache service wrapper around Django's cache backend.

This thin wrapper keeps use cases decoupled from the underlying cache
implementation (LocMemCache in tests, Redis in production).
"""

from typing import Any

from django.core.cache import cache


class CacheService:
    """Synchronous cache operations."""

    def get(self, key: str) -> Any | None:
        return cache.get(key)

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        cache.set(key, value, timeout=timeout)

    def delete(self, key: str) -> None:
        cache.delete(key)

    def exists(self, key: str) -> bool:
        return cache.get(key) is not None
