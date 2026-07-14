"""Event outbox app config."""

from django.apps import AppConfig


class EventOutboxConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.event_outbox"
    verbose_name = "Event Outbox"
