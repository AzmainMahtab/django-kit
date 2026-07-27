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

# Channels group backend. Redis is required for real deployments: the in-memory
# layer is per-process, so a group send from a Celery worker or a second web
# process would never reach a socket held by the first.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [os.getenv("CHANNEL_LAYER_URL", REDIS_URL)]},
    }
}
