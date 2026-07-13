"""Get car queries."""

from backend.apps.car.domain.exceptions import CarNotFoundError
from backend.apps.car.domain.models import Car
from backend.apps.car.domain.repository_interfaces import CarRepositoryInterface
from backend.shared.domain import UseCase


class GetCarByUuidUseCase(UseCase):
    """Pure read: fetch a car by UUID."""

    def __init__(self, car_repository: CarRepositoryInterface = None):
        if car_repository is None:
            from backend.apps.car.repositories.car_repository import CarRepository

            self.car_repo = CarRepository()
        else:
            self.car_repo = car_repository

    def execute(self, uuid: str) -> Car:
        car = self.car_repo.get_by_uuid(uuid)
        if car is None:
            raise CarNotFoundError(f"Car with uuid {uuid} not found.")
        return car
