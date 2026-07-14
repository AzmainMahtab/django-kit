"""Payment app config."""

from django.apps import AppConfig


class PaymentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.payment"

    def ready(self):
        pass
