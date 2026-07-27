"""Get car queries."""

from backend.apps.car.domain.exceptions import CarNotFoundError
from backend.apps.car.domain.models import Car
from backend.shared.domain import UseCase


class GetCarByUuidUseCase(UseCase):
    """Pure read: fetch a car by UUID."""

    def execute(self, uuid: str) -> Car:
        car = Car.objects.get_by_uuid(uuid)
        if car is None:
            raise CarNotFoundError(f"Car with uuid {uuid} not found.")
        return car
