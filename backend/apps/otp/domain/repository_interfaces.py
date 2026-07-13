"""OTP repository interfaces (ports)."""

from abc import ABC, abstractmethod

from backend.apps.otp.domain.models import OneTimePassword
from backend.apps.otp.domain.value_objects import OtpType


class OtpRepositoryInterface(ABC):
    @abstractmethod
    def create(self, otp: OneTimePassword) -> OneTimePassword:
        raise NotImplementedError

    @abstractmethod
    def get_latest_by_user_and_type(
        self, user_id: int, otp_type: OtpType
    ) -> OneTimePassword | None:
        raise NotImplementedError

    @abstractmethod
    def mark_used(self, otp_id: int) -> None:
        raise NotImplementedError
