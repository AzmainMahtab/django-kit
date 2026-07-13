"""Public API for the car module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.car.use_cases.commands.create_car import CreateCarUseCase
from backend.apps.car.use_cases.queries.get_car import GetCarByUuidUseCase
from backend.apps.car.use_cases.queries.list_cars import (
    ListCarsByOwnerUseCase,
    ListCarsUseCase,
)


class CarUseCases:
    """Facade exposed through the use-case registry."""

    def __init__(self):
        self.commands = CarCommands()
        self.queries = CarQueries()

    def create_car(self, **kwargs):
        return self.commands.create_car.execute(**kwargs)

    def get_car_by_uuid(self, **kwargs):
        return self.queries.get_car_by_uuid.execute(**kwargs)

    def list_cars_by_owner(self, **kwargs):
        return self.queries.list_cars_by_owner.execute(**kwargs)

    def list_cars(self, **kwargs):
        return self.queries.list_cars.execute(**kwargs)


class CarCommands:
    def __init__(self):
        self.create_car = CreateCarUseCase()


class CarQueries:
    def __init__(self):
        self.get_car_by_uuid = GetCarByUuidUseCase()
        self.list_cars_by_owner = ListCarsByOwnerUseCase()
        self.list_cars = ListCarsUseCase()
