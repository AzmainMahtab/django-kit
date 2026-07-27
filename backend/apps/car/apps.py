"""Car app config."""

from django.apps import AppConfig


class CarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.car"
