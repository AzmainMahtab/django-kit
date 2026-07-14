"""Promotion app config."""

from django.apps import AppConfig


class PromotionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.promotion"

    def ready(self):
        pass
