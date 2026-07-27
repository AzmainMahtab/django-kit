"""Django REST framework settings."""

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "backend.shared.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "120/minute",
        # Scoped throttle for OTP endpoints — stricter because brute-force
        # attacks against short codes are cheap.
        "otp": "5/minute",
        # Scoped throttle for authentication endpoints.
        "login": "10/minute",
        "refresh": "20/minute",
    },
    "DEFAULT_PAGINATION_CLASS": "backend.shared.pagination.CustomPagination",
    "DEFAULT_RENDERER_CLASSES": [
        "backend.shared.renderer.CustomJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "EXCEPTION_HANDLER": "backend.shared.exceptions.custom_exception_handler",
}
