"""Create car command."""

from backend.apps.car.domain.events import CarCreated
from backend.apps.car.domain.exceptions import CarAlreadyExistsError
from backend.apps.car.domain.models import Car
from backend.apps.car.domain.ports import OwnerFacade
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import NotFoundError


class CreateCarUseCase(UseCase):
    """Create a new car for an owner."""

    def __init__(
        self,
        event_bus: EventBus,
        owner_facade: OwnerFacade,
    ) -> None:
        self.event_bus = event_bus
        self.owner_facade = owner_facade

    def execute(
        self,
        owner_id: int,
        make: str,
        model: str,
        year: int,
        color: str,
        license_plate: str,
    ) -> Car:
        if Car.objects.get_by_license_plate(license_plate):
            raise CarAlreadyExistsError(
                f"A car with license plate '{license_plate}' already exists."
            )

        # Validate the owner exists via the injected facade (cross-module rule).
        try:
            self.owner_facade.get_owner_by_id(owner_id=owner_id)
        except Exception as exc:
            raise NotFoundError(f"Owner with id {owner_id} not found.") from exc

        car = Car.objects.create(
            owner_id=owner_id,
            make=make,
            model=model,
            year=year,
            color=color,
            license_plate=license_plate,
        )
        self.event_bus.publish(
            CarCreated(
                aggregate_id=car.id,
                data={
                    "car_id": car.id,
                    "owner_id": car.owner_id,
                    "license_plate": car.license_plate,
                },
            )
        )
        return car
