"""Re-export OTP domain models for Django discovery."""

from backend.apps.otp.domain.models import OneTimePassword

__all__ = ["OneTimePassword"]
