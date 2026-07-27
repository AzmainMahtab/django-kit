"""List cars queries."""

from backend.apps.car.domain.models import Car
from backend.shared.domain import UseCase


class ListCarsByOwnerUseCase(UseCase):
    """Pure read: list cars belonging to an owner."""

    def execute(self, owner_id: int):
        return Car.objects.list_by_owner(owner_id)


class ListCarsUseCase(UseCase):
    """Pure read: list all cars."""

    def execute(self):
        return Car.objects.list_all()
