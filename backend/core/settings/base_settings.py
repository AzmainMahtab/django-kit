"""Base Django settings for the modular monolith."""

import os
from pathlib import Path

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

from .celery_settings import *  # noqa: F403
from .cors_settings import *  # noqa: F403
from .database_settings import *  # noqa: F403
from .drf_settings import *  # noqa: F403
from .drf_spectacular_settings import *  # noqa: F403
from .redis_settings import *  # noqa: F403
from .storage_settings import *  # noqa: F403

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-in-production")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME_SECONDS = int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_SECONDS", "900"))
JWT_REFRESH_TOKEN_LIFETIME_SECONDS = int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME_SECONDS", "604800"))

# Secure by default: DEBUG must be opted into explicitly for local development.
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    # Must precede django.contrib.staticfiles so `runserver` serves ASGI and
    # WebSocket routes work in development.
    "daphne",
    # Django built-in
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
    "django_celery_beat",
    "channels",
    # Modular Monolith Apps
    "backend.apps.identity",
    "backend.apps.otp",
    "backend.apps.rbac",
    "backend.apps.owner",
    "backend.apps.car",
    "backend.apps.ordering",
    "backend.apps.notification",
    "backend.apps.event_outbox",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "backend.shared.metrics.MetricsMiddleware",
    "backend.shared.middleware.CorrelationIdMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.core.wsgi.application"
ASGI_APPLICATION = "backend.core.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "identity.User"

AUTHENTICATION_BACKENDS = [
    "backend.shared.admin_backend.RbacAdminBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Use Argon2 as the primary password hasher. PBKDF2 is kept as a fallback so
# legacy hashes remain verifiable.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Structured by default in production, human-readable in development. Both
# formats carry the X-Request-ID correlation ID set by CorrelationIdMiddleware,
# so a single request can be traced across web, Celery worker and beat output.
LOG_FORMAT = os.getenv("LOG_FORMAT", "console" if DEBUG else "json")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "backend.shared.middleware.RequestIdFilter",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} [{request_id}] {message}",
            "style": "{",
        },
        "json": {
            "()": "backend.shared.middleware.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "json" if LOG_FORMAT == "json" else "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}

# Production security hardening. These are opt-in via environment variables so
# local development continues to work without TLS.
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("DJANGO_SESSION_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("DJANGO_CSRF_COOKIE_SECURE", "False").lower() == "true"
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Sentry error tracking. Enabled only when SENTRY_DSN is set so local
# development and tests run without sending events.
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
    )
