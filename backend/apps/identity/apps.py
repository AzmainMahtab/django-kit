"""Identity app config."""

from django.apps import AppConfig


class IdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.identity"

    def ready(self):
        from backend.apps.identity.use_cases import IdentityUseCases
        from backend.shared.use_case_registry import registry

        registry.register("identity", IdentityUseCases())
