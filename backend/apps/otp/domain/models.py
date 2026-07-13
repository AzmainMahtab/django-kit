"""OTP domain models."""

from django.conf import settings
from django.db import models

from backend.apps.otp.domain.value_objects import OtpType


class OneTimePassword(models.Model):
    """Stored OTP with hashed code, type, and usage tracking."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
        db_index=True,
    )
    otp_type = models.CharField(
        max_length=32,
        choices=[(t.value, t.value) for t in OtpType],
        db_index=True,
    )
    code_hash = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "otp_one_time_password"
        ordering = ["-created_at"]

    @property
    def is_expired(self) -> bool:
        from datetime import UTC, datetime

        return datetime.now(UTC) > self.expires_at

    @property
    def ttl_seconds(self) -> int:
        from datetime import UTC, datetime

        remaining = int((self.expires_at - datetime.now(UTC)).total_seconds())
        return max(remaining, 0)
