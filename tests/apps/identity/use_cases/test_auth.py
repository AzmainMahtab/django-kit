"""Unit tests for identity authentication use cases."""

import pytest
from django.contrib.auth.hashers import make_password

from backend.apps.identity.domain.models import User
from backend.apps.identity.use_cases.commands.login import LoginUseCase
from backend.apps.identity.use_cases.commands.logout import LogoutUseCase
from backend.apps.identity.use_cases.commands.refresh_token import RefreshTokenUseCase
from backend.shared.exceptions import NotFoundError
from backend.shared.token_service import TokenService


class MockUserRepository:
    def __init__(self, users=None):
        self._users = {u.id: u for u in (users or [])}

    def get_by_email(self, email: str) -> User:
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        raise User.DoesNotExist()

    def get_by_id(self, user_id: int) -> User:
        if user_id in self._users:
            return self._users[user_id]
        raise User.DoesNotExist()

    def list_users(self, filters=None):
        return []

    def create(self, **kwargs):
        return User(**kwargs)

    def save(self, user, update_fields=None):
        return user

    def delete(self, user):
        pass


def _active_user():
    user = User(
        id=1,
        username="alice",
        email="alice@example.com",
        password=make_password("secret123"),
        is_active=True,
    )
    return user


def test_login_success():
    repo = MockUserRepository([_active_user()])
    use_case = LoginUseCase(user_repository=repo)

    result = use_case.execute(email="alice@example.com", password="secret123")

    assert "access_token" in result
    assert "refresh_token" in result


def test_login_invalid_password_raises():
    repo = MockUserRepository([_active_user()])
    use_case = LoginUseCase(user_repository=repo)

    with pytest.raises(Exception) as exc:
        use_case.execute(email="alice@example.com", password="wrong")

    assert exc.value.status_code == 401


def test_login_inactive_user_raises():
    user = _active_user()
    user.is_active = False
    repo = MockUserRepository([user])
    use_case = LoginUseCase(user_repository=repo)

    with pytest.raises(Exception) as exc:
        use_case.execute(email="alice@example.com", password="secret123")

    assert exc.value.status_code == 401


def test_refresh_token_success():
    user = _active_user()
    repo = MockUserRepository([user])
    token_service = TokenService()
    tokens = token_service.create_token_pair(user.id)

    use_case = RefreshTokenUseCase(user_repository=repo, token_service=token_service)
    new_tokens = use_case.execute(refresh_token=tokens["refresh_token"])

    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


def test_refresh_token_rejects_used_token():
    user = _active_user()
    repo = MockUserRepository([user])
    token_service = TokenService()
    tokens = token_service.create_token_pair(user.id)

    use_case = RefreshTokenUseCase(user_repository=repo, token_service=token_service)
    use_case.execute(refresh_token=tokens["refresh_token"])

    with pytest.raises(Exception) as exc:
        use_case.execute(refresh_token=tokens["refresh_token"])

    assert exc.value.status_code == 401


def test_logout_blacklists_tokens():
    user = _active_user()
    token_service = TokenService()
    tokens = token_service.create_token_pair(user.id)

    use_case = LogoutUseCase(token_service=token_service)
    use_case.execute(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"],
    )

    refresh_jti = token_service.decode(tokens["refresh_token"])["jti"]
    access_jti = token_service.decode(tokens["access_token"])["jti"]
    assert use_case.cache.exists(f"token:blacklist:{refresh_jti}")
    assert use_case.cache.exists(f"token:blacklist:{access_jti}")


def test_get_profile_success():
    from backend.apps.identity.use_cases.queries.get_profile import GetProfileUseCase

    repo = MockUserRepository([_active_user()])
    use_case = GetProfileUseCase(user_repository=repo)

    result = use_case.execute(user_id=1)
    assert result.email == "alice@example.com"


def test_get_profile_missing_user_raises():
    from backend.apps.identity.use_cases.queries.get_profile import GetProfileUseCase

    repo = MockUserRepository([])
    use_case = GetProfileUseCase(user_repository=repo)

    with pytest.raises(NotFoundError):
        use_case.execute(user_id=99)
