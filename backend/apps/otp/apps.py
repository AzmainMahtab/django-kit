"""OTP app config."""

from django.apps import AppConfig


class OtpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.otp"
