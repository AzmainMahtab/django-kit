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
from backend.apps.otp.domain.value_objects import OtpType
from backend.apps.otp.use_cases.commands.generate_otp import GenerateOtpUseCase
from backend.apps.otp.use_cases.commands.validate_otp import ValidateOtpUseCase
from backend.shared.cache_service import CacheService
from backend.shared.event_bus import EventBus

pytestmark = pytest.mark.django_db


def _create_otp(code: str = "654321", expired: bool = False, used: bool = False):
    expires_at = (
        datetime.now(UTC) - timedelta(seconds=1)
        if expired
        else datetime.now(UTC) + timedelta(minutes=5)
    )
    return OneTimePassword.objects.create(
        user_id=1,
        otp_type=OtpType.LOGIN.value,
        code_hash=make_password(code),
        is_used=used,
        expires_at=expires_at,
    )


def test_generate_otp_returns_code():
    bus = EventBus()
    use_case = GenerateOtpUseCase(event_bus=bus)

    result = use_case.execute(user_id=1, otp_type=OtpType.LOGIN)

    assert result["code"].isdigit()
    assert len(result["code"]) == 6
    assert result["expires_at"] > datetime.now(UTC)


def test_validate_otp_with_cached_code():
    cache = CacheService()
    bus = EventBus()
    generate = GenerateOtpUseCase(event_bus=bus, cache_service=cache)
    result = generate.execute(user_id=1, otp_type=OtpType.LOGIN)

    validate = ValidateOtpUseCase(event_bus=bus, cache_service=cache)
    outcome = validate.execute(user_id=1, otp_type=OtpType.LOGIN, code=result["code"])

    assert outcome["success"] is True


def test_validate_otp_with_db_fallback():
    _create_otp(code="654321")
    bus = EventBus()
    validate = ValidateOtpUseCase(event_bus=bus)

    outcome = validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="654321")
    assert outcome["success"] is True


def test_validate_invalid_code_raises():
    _create_otp(code="654321")
    bus = EventBus()
    validate = ValidateOtpUseCase(event_bus=bus)

    with pytest.raises(InvalidOtpError):
        validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="000000")


def test_validate_used_otp_raises():
    _create_otp(code="654321", used=True)
    bus = EventBus()
    validate = ValidateOtpUseCase(event_bus=bus)

    with pytest.raises(OtpAlreadyUsedError):
        validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="654321")


def test_validate_expired_otp_raises():
    _create_otp(code="654321", expired=True)
    bus = EventBus()
    validate = ValidateOtpUseCase(event_bus=bus)

    with pytest.raises(OtpExpiredError):
        validate.execute(user_id=1, otp_type=OtpType.LOGIN, code="654321")


def test_generate_otp_publishes_event():
    bus = EventBus()
    received = []
    bus.subscribe("otp.generated", received.append)
    use_case = GenerateOtpUseCase(event_bus=bus)

    use_case.execute(user_id=1, otp_type=OtpType.LOGIN)

    assert len(received) == 1
    assert received[0].data["user_id"] == 1
