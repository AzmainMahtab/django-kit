"""Public API for the car module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.car.domain.ports import OwnerFacade
from backend.apps.car.use_cases.commands.create_car import CreateCarUseCase
from backend.apps.car.use_cases.queries.get_car import GetCarByUuidUseCase
from backend.apps.car.use_cases.queries.list_cars import (
    ListCarsByOwnerUseCase,
    ListCarsUseCase,
)
from backend.shared.event_bus import EventBus


class CarUseCases:
    """Facade exposed through the dependency container."""

    def __init__(self, event_bus: EventBus, owner_facade: OwnerFacade) -> None:
        self.event_bus = event_bus
        self.commands = CarCommands(
            event_bus=event_bus,
            owner_facade=owner_facade,
        )
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
    def __init__(self, event_bus: EventBus, owner_facade: OwnerFacade) -> None:
        self.create_car = CreateCarUseCase(
            event_bus=event_bus,
            owner_facade=owner_facade,
        )


class CarQueries:
    def __init__(self):
        self.get_car_by_uuid = GetCarByUuidUseCase()
        self.list_cars_by_owner = ListCarsByOwnerUseCase()
        self.list_cars = ListCarsUseCase()
