"""Create car command."""

from backend.apps.car.domain.exceptions import CarAlreadyExistsError
from backend.apps.car.domain.models import Car
from backend.apps.car.domain.repository_interfaces import CarRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError
from backend.shared.use_case_registry import get_owner


class CreateCarUseCase(UseCase):
    """Create a new car for an owner."""

    def __init__(self, car_repository: CarRepositoryInterface = None):
        if car_repository is None:
            from backend.apps.car.repositories.car_repository import CarRepository

            self.car_repo = CarRepository()
        else:
            self.car_repo = car_repository

    def execute(
        self,
        owner_id: int,
        make: str,
        model: str,
        year: int,
        color: str,
        license_plate: str,
    ) -> Car:
        existing = self.car_repo.get_by_license_plate(license_plate)
        if existing:
            raise CarAlreadyExistsError(
                f"A car with license plate '{license_plate}' already exists."
            )

        # Validate the owner exists via the registry (cross-module rule).
        try:
            get_owner().get_owner_by_id(owner_id=owner_id)
        except Exception as exc:
            raise NotFoundError(f"Owner with id {owner_id} not found.") from exc

        car = Car(
            owner_id=owner_id,
            make=make,
            model=model,
            year=year,
            color=color,
            license_plate=license_plate,
        )

        return self.car_repo.create(car)
