"""Shared pytest fixtures for django-kit."""

import pytest


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Ensure throttle counts (and any other cache state) do not leak between tests."""
    from django.core.cache import cache

    cache.clear()
