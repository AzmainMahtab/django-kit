"""Database settings."""

import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "django_init"),
        "USER": os.getenv("POSTGRES_USER", "django_init"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "django_init"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}
