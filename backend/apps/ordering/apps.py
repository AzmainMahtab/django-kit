"""Ordering app config."""

from django.apps import AppConfig


class OrderingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.ordering"
