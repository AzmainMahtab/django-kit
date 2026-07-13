"""Unit tests for CreateUserUseCase."""

import pytest

from backend.apps.identity.domain.models import User
from backend.apps.identity.use_cases.commands.create_user import CreateUserUseCase
from backend.shared.exceptions import BusinessValidationError


class MockUserRepository:
    def __init__(self, existing_emails=None, existing_usernames=None):
        self._users = {}
        self._next_id = 1
        self._existing_emails = set(existing_emails or [])
        self._existing_usernames = set(existing_usernames or [])

    def list_users(self, filters=None):
        class QS:
            @staticmethod
            def exists():
                if filters and "email__iexact" in filters:
                    return filters["email__iexact"].lower() in self._existing_emails
                if filters and "username__iexact" in filters:
                    return filters["username__iexact"].lower() in self._existing_usernames
                return bool(self._users)
        return QS()

    def create(self, **kwargs):
        user = User(**kwargs)
        user.id = self._next_id
        self._next_id += 1
        self._users[user.id] = user
        return user


def test_create_user_success():
    repo = MockUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    result = use_case.execute(
        username="jane_doe",
        email="jane@example.com",
        password="super-secret-123",
    )

    assert result.username == "jane_doe"
    assert result.email == "jane@example.com"


def test_create_user_duplicate_email_raises():
    repo = MockUserRepository(existing_emails=["jane@example.com"])
    use_case = CreateUserUseCase(user_repository=repo)

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(
            username="jane_doe2",
            email="jane@example.com",
            password="super-secret-123",
        )

    assert "email" in str(exc.value)
