"""Unit tests for identity authentication use cases."""

import pytest

from backend.apps.identity.domain.models import User
from backend.apps.identity.use_cases.commands.login import LoginUseCase
from backend.apps.identity.use_cases.commands.logout import LogoutUseCase
from backend.apps.identity.use_cases.commands.refresh_token import RefreshTokenUseCase
from backend.apps.identity.use_cases.queries.get_profile import GetProfileUseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import NotFoundError
from backend.shared.token_service import TokenService

pytestmark = pytest.mark.django_db


def _active_user():
    return User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="secret123",
        is_active=True,
    )


def test_login_success():
    _active_user()
    bus = EventBus()
    use_case = LoginUseCase(event_bus=bus)

    result = use_case.execute(email="alice@example.com", password="secret123")

    assert "access_token" in result
    assert "refresh_token" in result


def test_login_invalid_password_raises():
    _active_user()
    bus = EventBus()
    use_case = LoginUseCase(event_bus=bus)

    with pytest.raises(Exception) as exc:
        use_case.execute(email="alice@example.com", password="wrong")

    assert exc.value.status_code == 401


def test_login_inactive_user_raises():
    user = _active_user()
    user.is_active = False
    user.save(update_fields=["is_active"])
    bus = EventBus()
    use_case = LoginUseCase(event_bus=bus)

    with pytest.raises(Exception) as exc:
        use_case.execute(email="alice@example.com", password="secret123")

    assert exc.value.status_code == 401


def test_refresh_token_success():
    user = _active_user()
    token_service = TokenService()
    tokens = token_service.create_token_pair(user.id)

    bus = EventBus()
    use_case = RefreshTokenUseCase(
        event_bus=bus,
        token_service=token_service,
    )
    new_tokens = use_case.execute(refresh_token=tokens["refresh_token"])

    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


def test_refresh_token_rejects_used_token():
    user = _active_user()
    token_service = TokenService()
    tokens = token_service.create_token_pair(user.id)

    bus = EventBus()
    use_case = RefreshTokenUseCase(
        event_bus=bus,
        token_service=token_service,
    )
    use_case.execute(refresh_token=tokens["refresh_token"])

    with pytest.raises(Exception) as exc:
        use_case.execute(refresh_token=tokens["refresh_token"])

    assert exc.value.status_code == 401


def test_logout_blacklists_tokens():
    user = _active_user()
    token_service = TokenService()
    tokens = token_service.create_token_pair(user.id)

    bus = EventBus()
    use_case = LogoutUseCase(event_bus=bus, token_service=token_service)
    use_case.execute(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"],
    )

    refresh_jti = token_service.decode(tokens["refresh_token"])["jti"]
    access_jti = token_service.decode(tokens["access_token"])["jti"]
    assert use_case.cache.exists(f"token:blacklist:{refresh_jti}")
    assert use_case.cache.exists(f"token:blacklist:{access_jti}")


def test_get_profile_success():
    user = _active_user()
    use_case = GetProfileUseCase()

    result = use_case.execute(user_id=user.id)
    assert result.email == "alice@example.com"


def test_get_profile_missing_user_raises():
    use_case = GetProfileUseCase()

    with pytest.raises(NotFoundError):
        use_case.execute(user_id=99)
