"""OTP app config."""

from django.apps import AppConfig


class OtpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.otp"

    def ready(self):
        from backend.apps.otp.use_cases import OtpUseCases
        from backend.shared.use_case_registry import registry

        registry.register("otp", OtpUseCases())
