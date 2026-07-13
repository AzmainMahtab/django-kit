"""Ordering app config."""

from django.apps import AppConfig


class OrderingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.ordering"

    def ready(self):
        from backend.apps.ordering.use_cases import OrderingUseCases
        from backend.shared.use_case_registry import registry

        registry.register("ordering", OrderingUseCases())
