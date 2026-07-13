"""Unit tests for CreateCarUseCase."""

import pytest

from backend.apps.car.domain.exceptions import CarAlreadyExistsError
from backend.apps.car.domain.models import Car
from backend.apps.car.use_cases.commands.create_car import CreateCarUseCase


class MockCarRepository:
    def __init__(self, existing_license_plates=None):
        self._cars = {}
        self._next_id = 1
        self._existing_license_plates = set(existing_license_plates or [])

    def get_by_id(self, car_id: int) -> Car:
        return self._cars[car_id]

    def get_by_uuid(self, uuid: str):
        for car in self._cars.values():
            if str(car.uuid) == str(uuid):
                return car
        return None

    def get_by_license_plate(self, license_plate: str):
        if license_plate in self._existing_license_plates:
            car = Car(
                owner_id=1,
                make="Toyota",
                model="Camry",
                year=2020,
                color="Blue",
                license_plate=license_plate,
            )
            car.id = self._next_id
            return car
        return None

    def create(self, car: Car) -> Car:
        car.id = self._next_id
        self._next_id += 1
        self._cars[car.id] = car
        self._existing_license_plates.add(car.license_plate)
        return car

    def list_by_owner(self, owner_id: int):
        return [c for c in self._cars.values() if c.owner_id == owner_id]

    def list_all(self):
        return list(self._cars.values())


class MockOwnerUseCases:
    def get_owner_by_id(self, owner_id: int):
        if owner_id == 99:
            raise Exception("Owner not found")
        return {"id": owner_id}


def test_create_car_success(monkeypatch):
    repo = MockCarRepository()
    use_case = CreateCarUseCase(car_repository=repo)
    monkeypatch.setattr(
        "backend.apps.car.use_cases.commands.create_car.get_owner",
        lambda: MockOwnerUseCases(),
    )

    car = use_case.execute(
        owner_id=1,
        make="Toyota",
        model="Camry",
        year=2020,
        color="Blue",
        license_plate="ABC123",
    )

    assert car.owner_id == 1
    assert car.make == "Toyota"
    assert car.license_plate == "ABC123"


def test_create_car_duplicate_license_plate_raises(monkeypatch):
    repo = MockCarRepository(existing_license_plates=["ABC123"])
    use_case = CreateCarUseCase(car_repository=repo)
    monkeypatch.setattr(
        "backend.apps.car.use_cases.commands.create_car.get_owner",
        lambda: MockOwnerUseCases(),
    )

    with pytest.raises(CarAlreadyExistsError) as exc:
        use_case.execute(
            owner_id=1,
            make="Toyota",
            model="Camry",
            year=2020,
            color="Blue",
            license_plate="ABC123",
        )

    assert "already exists" in str(exc.value)


def test_create_car_missing_owner_raises(monkeypatch):
    repo = MockCarRepository()
    use_case = CreateCarUseCase(car_repository=repo)
    monkeypatch.setattr(
        "backend.apps.car.use_cases.commands.create_car.get_owner",
        lambda: MockOwnerUseCases(),
    )

    with pytest.raises(Exception) as exc:
        use_case.execute(
            owner_id=99,
            make="Toyota",
            model="Camry",
            year=2020,
            color="Blue",
            license_plate="XYZ789",
        )

    assert "not found" in str(exc.value).lower()
