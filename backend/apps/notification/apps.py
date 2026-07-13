"""Notification app config."""

from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.notification"

    def ready(self):
        from backend.apps.notification.infrastructure.event_handlers import (
            register_notification_handlers,
        )
        from backend.shared.use_case_registry import registry
        from backend.apps.notification.use_cases import NotificationUseCases

        registry.register("notification", NotificationUseCases())
        register_notification_handlers()
