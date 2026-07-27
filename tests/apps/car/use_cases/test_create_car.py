"""Unit tests for CreateCarUseCase."""

import pytest

from backend.apps.car.domain.exceptions import CarAlreadyExistsError
from backend.apps.car.domain.models import Car
from backend.apps.car.use_cases.commands.create_car import CreateCarUseCase
from backend.apps.owner.domain.models import Owner
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import NotFoundError

pytestmark = pytest.mark.django_db


class MockOwnerFacade:
    """Test double for the owner module facade port."""

    def __init__(self, owner: Owner | None = None):
        self.owner = owner

    def get_owner_by_id(self, owner_id: int):
        if self.owner is None or self.owner.id != owner_id:
            raise Owner.DoesNotExist("Owner not found")
        return self.owner


def test_create_car_success():
    owner = Owner.objects.create(user_id=1, address="123 Main St")
    bus = EventBus()
    use_case = CreateCarUseCase(
        event_bus=bus,
        owner_facade=MockOwnerFacade(owner),
    )

    car = use_case.execute(
        owner_id=owner.id,
        make="Toyota",
        model="Camry",
        year=2020,
        color="Blue",
        license_plate="ABC123",
    )

    assert car.owner_id == owner.id
    assert car.make == "Toyota"
    assert car.license_plate == "ABC123"


def test_create_car_duplicate_license_plate_raises():
    owner = Owner.objects.create(user_id=1, address="123 Main St")
    Car.objects.create(
        owner_id=owner.id,
        make="Toyota",
        model="Camry",
        year=2020,
        color="Blue",
        license_plate="ABC123",
    )
    bus = EventBus()
    use_case = CreateCarUseCase(
        event_bus=bus,
        owner_facade=MockOwnerFacade(owner),
    )

    with pytest.raises(CarAlreadyExistsError) as exc:
        use_case.execute(
            owner_id=owner.id,
            make="Toyota",
            model="Camry",
            year=2020,
            color="Blue",
            license_plate="ABC123",
        )

    assert "already exists" in str(exc.value)


def test_create_car_missing_owner_raises():
    bus = EventBus()
    use_case = CreateCarUseCase(
        event_bus=bus,
        owner_facade=MockOwnerFacade(),
    )

    with pytest.raises(NotFoundError) as exc:
        use_case.execute(
            owner_id=99,
            make="Toyota",
            model="Camry",
            year=2020,
            color="Blue",
            license_plate="XYZ789",
        )

    assert "not found" in str(exc.value).lower()


def test_create_car_publishes_event():
    owner = Owner.objects.create(user_id=1, address="123 Main St")
    bus = EventBus()
    received = []
    bus.subscribe("car.car_created", received.append)
    use_case = CreateCarUseCase(
        event_bus=bus,
        owner_facade=MockOwnerFacade(owner),
    )

    car = use_case.execute(
        owner_id=owner.id,
        make="Toyota",
        model="Camry",
        year=2020,
        color="Blue",
        license_plate="ABC123",
    )

    assert len(received) == 1
    assert received[0].aggregate_id == car.id
