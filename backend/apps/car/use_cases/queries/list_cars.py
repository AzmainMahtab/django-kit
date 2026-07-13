"""List cars queries."""

from backend.apps.car.domain.repository_interfaces import CarRepositoryInterface
from backend.shared.domain import UseCase


class ListCarsByOwnerUseCase(UseCase):
    """Pure read: list cars belonging to an owner."""

    def __init__(self, car_repository: CarRepositoryInterface = None):
        if car_repository is None:
            from backend.apps.car.repositories.car_repository import CarRepository

            self.car_repo = CarRepository()
        else:
            self.car_repo = car_repository

    def execute(self, owner_id: int):
        return self.car_repo.list_by_owner(owner_id)


class ListCarsUseCase(UseCase):
    """Pure read: list all cars."""

    def __init__(self, car_repository: CarRepositoryInterface = None):
        if car_repository is None:
            from backend.apps.car.repositories.car_repository import CarRepository

            self.car_repo = CarRepository()
        else:
            self.car_repo = car_repository

    def execute(self):
        return self.car_repo.list_all()
