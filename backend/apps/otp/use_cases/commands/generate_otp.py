"""Generate OTP command."""

import secrets
from datetime import UTC, datetime, timedelta

from django.contrib.auth.hashers import make_password

from backend.apps.otp.domain.events import OtpGenerated
from backend.apps.otp.domain.models import OneTimePassword
from backend.apps.otp.domain.repository_interfaces import OtpRepositoryInterface
from backend.apps.otp.domain.value_objects import OTP_EXPIRY_SECONDS, OTP_LENGTH, OtpType
from backend.shared.cache_service import CacheService
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus


class GenerateOtpUseCase(UseCase):
    """Generate a one-time password for a user and store it securely."""

    def __init__(
        self,
        otp_repository: OtpRepositoryInterface = None,
        cache_service: CacheService = None,
    ):
        if otp_repository is None:
            from backend.apps.otp.repositories.otp_repository import OtpRepository
            self.otp_repo = OtpRepository()
        else:
            self.otp_repo = otp_repository
        self.cache = cache_service or CacheService()

    def execute(self, user_id: int, otp_type: OtpType) -> dict:
        length = OTP_LENGTH[otp_type]
        ttl = OTP_EXPIRY_SECONDS[otp_type]

        code = "".join(str(secrets.randbelow(10)) for _ in range(length))
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl)

        otp = OneTimePassword(
            user_id=user_id,
            otp_type=otp_type.value,
            code_hash=make_password(code),
            expires_at=expires_at,
        )
        otp = self.otp_repo.create(otp)

        cache_key = self._cache_key(user_id, otp_type)
        self.cache.set(cache_key, {"code": code, "otp_id": otp.id}, timeout=ttl)

        event_bus.publish(
            OtpGenerated(
                aggregate_id=user_id,
                data={"user_id": user_id, "otp_type": otp_type.value, "otp_id": otp.id},
            )
        )

        return {
            "otp_id": otp.id,
            "code": code,
            "expires_at": expires_at,
        }

    @staticmethod
    def _cache_key(user_id: int, otp_type: OtpType) -> str:
        return f"otp:{user_id}:{otp_type.value}"
