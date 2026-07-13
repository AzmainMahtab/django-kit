"""Car app config."""

from django.apps import AppConfig


class CarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.car"

    def ready(self):
        from backend.apps.car.use_cases import CarUseCases
        from backend.shared.use_case_registry import registry

        registry.register("car", CarUseCases())
