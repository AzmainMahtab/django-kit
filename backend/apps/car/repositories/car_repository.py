"""Django ORM implementation of the car repository."""

from typing import Iterable

from django.db import IntegrityError

from backend.apps.car.domain.exceptions import CarAlreadyExistsError
from backend.apps.car.domain.models import Car
from backend.apps.car.domain.repository_interfaces import CarRepositoryInterface


class CarRepository(CarRepositoryInterface):
    """Implements CarRepositoryInterface using Django ORM."""

    def get_by_id(self, car_id: int) -> Car:
        return Car.objects.get(pk=car_id)

    def get_by_uuid(self, uuid: str) -> Car | None:
        try:
            return Car.objects.get(uuid=uuid)
        except Car.DoesNotExist:
            return None

    def get_by_license_plate(self, license_plate: str) -> Car | None:
        try:
            return Car.objects.get(license_plate=license_plate)
        except Car.DoesNotExist:
            return None

    def create(self, car: Car) -> Car:
        try:
            car.save()
        except IntegrityError as exc:
            if "license_plate" in str(exc).lower() or "unique" in str(exc).lower():
                raise CarAlreadyExistsError(
                    f"A car with license plate '{car.license_plate}' already exists."
                ) from exc
            raise
        return car

    def list_by_owner(self, owner_id: int) -> Iterable[Car]:
        return Car.objects.filter(owner_id=owner_id).order_by("-created_at")

    def list_all(self) -> Iterable[Car]:
        return Car.objects.all().order_by("-created_at")
