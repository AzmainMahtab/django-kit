"""RBAC app config."""

from django.apps import AppConfig


class RbacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.rbac"

    def ready(self):
        from backend.apps.rbac.use_cases import RbacUseCases
        from backend.shared.use_case_registry import registry

        registry.register("rbac", RbacUseCases())
