"""Validate OTP command."""

from django.contrib.auth.hashers import check_password

from backend.apps.otp.domain.events import OtpValidated
from backend.apps.otp.domain.exceptions import InvalidOtpError, OtpAlreadyUsedError, OtpExpiredError
from backend.apps.otp.domain.models import OneTimePassword
from backend.apps.otp.domain.value_objects import OtpType
from backend.shared.cache_service import CacheService
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus


class ValidateOtpUseCase(UseCase):
    """Validate a one-time password for a user and type."""

    def __init__(
        self,
        event_bus: EventBus,
        cache_service: CacheService | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.cache = cache_service or CacheService()

    def execute(self, user_id: int, otp_type: OtpType, code: str) -> dict:
        cache_key = self._cache_key(user_id, otp_type)
        cached = self.cache.get(cache_key)

        if cached and cached.get("code") == code:
            otp_id = cached["otp_id"]
            OneTimePassword.objects.filter(pk=otp_id).update(is_used=True)
            self.cache.delete(cache_key)
            self._publish_event(user_id, otp_type, otp_id)
            return {"success": True, "otp_id": otp_id}

        otp = OneTimePassword.objects.get_latest_by_user_and_type(user_id, otp_type)
        if otp is None:
            raise InvalidOtpError("No valid OTP found for this user and type.")

        if otp.is_used:
            raise OtpAlreadyUsedError("OTP has already been used.")

        if otp.is_expired:
            raise OtpExpiredError("OTP has expired.")

        if not check_password(code, otp.code_hash):
            raise InvalidOtpError("Invalid OTP code.")

        OneTimePassword.objects.filter(pk=otp.id).update(is_used=True)
        self.cache.delete(cache_key)
        self._publish_event(user_id, otp_type, otp.id)

        return {"success": True, "otp_id": otp.id}

    @staticmethod
    def _cache_key(user_id: int, otp_type: OtpType) -> str:
        return f"otp:{user_id}:{otp_type.value}"

    def _publish_event(self, user_id: int, otp_type: OtpType, otp_id: int) -> None:
        self.event_bus.publish(
            OtpValidated(
                aggregate_id=user_id,
                data={"user_id": user_id, "otp_type": otp_type.value, "otp_id": otp_id},
            )
        )
