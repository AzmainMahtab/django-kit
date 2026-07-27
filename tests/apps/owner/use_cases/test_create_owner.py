"""Unit tests for CreateOwnerUseCase."""

import pytest

from backend.apps.owner.domain.exceptions import OwnerAlreadyExistsError
from backend.apps.owner.domain.models import Owner
from backend.apps.owner.use_cases.commands.create_owner import CreateOwnerUseCase
from backend.shared.event_bus import EventBus

pytestmark = pytest.mark.django_db


def test_create_owner_success():
    bus = EventBus()
    use_case = CreateOwnerUseCase(event_bus=bus)

    owner = use_case.execute(user_id=1, address="123 Main St")

    assert owner.user_id == 1
    assert owner.address == "123 Main St"


def test_create_owner_duplicate_user_raises():
    Owner.objects.create(user_id=1, address="123 Existing St")
    bus = EventBus()
    use_case = CreateOwnerUseCase(event_bus=bus)

    with pytest.raises(OwnerAlreadyExistsError) as exc:
        use_case.execute(user_id=1, address="123 Main St")

    assert "already exists" in str(exc.value)


def test_create_owner_publishes_event():
    bus = EventBus()
    received = []
    bus.subscribe("owner.owner_created", received.append)
    use_case = CreateOwnerUseCase(event_bus=bus)

    owner = use_case.execute(user_id=1, address="123 Main St")

    assert len(received) == 1
    assert received[0].aggregate_id == owner.id
    assert received[0].data["user_id"] == 1
