"""Unit tests for CreateUserUseCase."""

import pytest

from backend.apps.identity.domain.models import User
from backend.apps.identity.use_cases.commands.create_user import CreateUserUseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError

pytestmark = pytest.mark.django_db


def test_create_user_success():
    bus = EventBus()
    use_case = CreateUserUseCase(event_bus=bus)

    result = use_case.execute(
        username="jane_doe",
        email="jane@example.com",
        password="super-secret-123",
    )

    assert result.username == "jane_doe"
    assert result.email == "jane@example.com"


def test_create_user_duplicate_email_raises():
    User.objects.create_user(
        username="existing",
        email="jane@example.com",
        password="secret123",
    )
    bus = EventBus()
    use_case = CreateUserUseCase(event_bus=bus)

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(
            username="jane_doe2",
            email="jane@example.com",
            password="super-secret-123",
        )

    assert "email" in str(exc.value)


def test_create_user_publishes_event():
    bus = EventBus()
    received = []
    bus.subscribe("identity.user_created", received.append)
    use_case = CreateUserUseCase(event_bus=bus)

    result = use_case.execute(
        username="jane_doe",
        email="jane@example.com",
        password="super-secret-123",
    )

    assert len(received) == 1
    assert received[0].aggregate_id == result.id
