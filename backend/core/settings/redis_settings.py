"""Redis settings."""

import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Use LocMemCache when django-redis is not installed.
# Switch to django_redis.cache.RedisCache when scaling out.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
