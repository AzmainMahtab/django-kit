"""Django ORM implementation of the OTP repository."""

from backend.apps.otp.domain.models import OneTimePassword
from backend.apps.otp.domain.repository_interfaces import OtpRepositoryInterface
from backend.apps.otp.domain.value_objects import OtpType


class OtpRepository(OtpRepositoryInterface):
    """Implements OtpRepositoryInterface using Django ORM."""

    def create(self, otp: OneTimePassword) -> OneTimePassword:
        otp.save()
        return otp

    def get_latest_by_user_and_type(
        self, user_id: int, otp_type: OtpType
    ) -> OneTimePassword | None:
        return (
            OneTimePassword.objects.filter(user_id=user_id, otp_type=otp_type.value)
            .order_by("-created_at")
            .first()
        )

    def mark_used(self, otp_id: int) -> None:
        OneTimePassword.objects.filter(pk=otp_id).update(is_used=True)
