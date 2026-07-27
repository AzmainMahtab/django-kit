"""OTP domain models."""

from typing import cast

from django.db import models

from backend.apps.otp.domain.value_objects import OtpType


class OneTimePasswordManager(models.Manager):
    def get_latest_by_user_and_type(
        self, user_id: int, otp_type: OtpType
    ) -> "OneTimePassword | None":
        result = (
            self.get_queryset()
            .filter(user_id=user_id, otp_type=otp_type.value)
            .order_by("-created_at")
            .first()
        )
        return cast("OneTimePassword | None", result)


class OneTimePassword(models.Model):
    """Stored OTP with hashed code, type, and usage tracking."""

    objects = OneTimePasswordManager()

    user_id = models.IntegerField(db_index=True)
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
        ordering = ("-created_at",)

    @property
    def is_expired(self) -> bool:
        from datetime import UTC, datetime

        return datetime.now(UTC) > self.expires_at

    @property
    def ttl_seconds(self) -> int:
        from datetime import UTC, datetime

        remaining = int((self.expires_at - datetime.now(UTC)).total_seconds())
        return max(remaining, 0)
