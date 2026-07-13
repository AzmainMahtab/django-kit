"""Unit tests for OTP use cases."""

from datetime import UTC, datetime, timedelta

import pytest
from django.contrib.auth.hashers import make_password

from backend.apps.otp.domain.exceptions import (
    InvalidOtpError,
    OtpAlreadyUsedError,
    OtpExpiredError,
)
from backend.apps.otp.domain.models import OneTimePassword
from backend.apps.otp.domain.repository_interfaces import OtpRepositoryInterface
from backend.apps.otp.domain.value_objects import OtpType
from backend.apps.otp.use_cases.commands.generate_otp import GenerateOtpUseCase
from backend.apps.otp.use_cases.commands.validate_otp import ValidateOtpUseCase
from backend.shared.cache_service import CacheService


class MockOtpRepository(OtpRepositoryInterface):
    def __init__(self):
        self._records: dict[int, OneTimePassword] = {}
        self._next_id = 1

    def create(self, otp: OneTimePassword) -> OneTimePassword:
        otp.id = self._next_id
        self._next_id += 1
        self._records[otp.id] = otp
        return otp

    def get_latest_by_user_and_type(
        self, user_id: int, otp_type: OtpType
    ) -> OneTimePassword | None:
        matches = [
            otp
            for otp in self._records.values()
            if otp.user_id == user_id and otp.otp_type == otp_type.value
        ]
        return max(matches, key=lambda o: o.created_at) if matches else None

    def mark_used(self, otp_id: int) -> None:
        if otp_id in self._records:
            self._records[otp_id].is_used = True


def _repo_with_otp(code: str = "123456", expired: bool = False, used: bool = False):
    repo = MockOtpRepository()
    expires_at = (
        datetime.now(UTC) - timedelta(seconds=1)
        if expired
        else datetime.now(UTC) + timedelta(minutes=5)
    )
    otp = OneTimePassword(
        id=1,
        user_id=1,
        otp_type=OtpType.LOGIN.value,
        code_hash=make_password(code),
        is_used=used,
        expires_at=expires_at,
        created_at=datetime.now(UTC),
    )
    repo._records[1] = otp
    return repo


def test_generate_otp_returns_code():
    repo = MockOtpRepository()
    use_case = GenerateOtpUseCase(otp_repository=repo)

    result = use_case.execute(user_id=1, otp_type=OtpType.LOGIN)

    assert result["code"].isdigit()
    assert len(result["code"]) == 6
    assert result["expires_at"] > datetime.now(UTC)


def test_validate_otp_with_cached_code():
    repo = MockOtpRepository()
    cache = CacheService()
    generate = GenerateOtpUseCase(otp_repository=repo, cache_service=cache)
    result = generate.execute(user_id=1, otp_type=OtpType.LOGIN)

    validate = ValidateOtpUseCase(otp_repository=repo, cache_service=cache)
    outcome = validate.execute(user_id=1, otp_type=OtpType.LOGIN, code=result["code"])

    assert outcome["success"] is True


def test_validate_otp_with_db_fallback():
    repo = _repo_with_otp(code="654321")
    cache = CacheService()
    validate = ValidateOtpUseCase(otp_repository=repo, cache_service=cache)

    outcome = validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="654321")
    assert outcome["success"] is True


def test_validate_invalid_code_raises():
    repo = _repo_with_otp(code="654321")
    validate = ValidateOtpUseCase(otp_repository=repo)

    with pytest.raises(InvalidOtpError):
        validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="000000")


def test_validate_used_otp_raises():
    repo = _repo_with_otp(code="654321", used=True)
    validate = ValidateOtpUseCase(otp_repository=repo)

    with pytest.raises(OtpAlreadyUsedError):
        validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="654321")


def test_validate_expired_otp_raises():
    repo = _repo_with_otp(code="654321", expired=True)
    validate = ValidateOtpUseCase(otp_repository=repo)

    with pytest.raises(OtpExpiredError):
        validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="654321")
