"""Owner app config."""

from django.apps import AppConfig


class OwnerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.owner"

    def ready(self):
        from backend.apps.owner.use_cases import OwnerUseCases
        from backend.shared.use_case_registry import registry

        registry.register("owner", OwnerUseCases())
