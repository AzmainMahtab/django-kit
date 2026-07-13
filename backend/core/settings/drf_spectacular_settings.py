"""drf-spectacular OpenAPI settings."""

SPECTACULAR_SETTINGS = {
    "TITLE": "Django Init API",
    "DESCRIPTION": "Modular Monolith starter kit for Django",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SCHEMA_PATH_PREFIX": r"/api/",
    "ENFORCE_SCHEMA_REQUIREMENT": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "Identity", "description": "Users, authentication, addresses"},
        {"name": "OTP", "description": "One-time password generation and validation"},
        {"name": "RBAC", "description": "Roles, permissions, and user-role assignments"},
        {"name": "Owner", "description": "Owner profiles linked to users"},
        {"name": "Car", "description": "Cars belonging to owners"},
    ],
}
