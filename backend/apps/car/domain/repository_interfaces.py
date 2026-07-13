"""Car repository interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Iterable

from backend.apps.car.domain.models import Car


class CarRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, car_id: int) -> Car:
        """Return a car by primary key or raise Car.DoesNotExist."""
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Car | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_license_plate(self, license_plate: str) -> Car | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, car: Car) -> Car:
        raise NotImplementedError

    @abstractmethod
    def list_by_owner(self, owner_id: int) -> Iterable[Car]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Iterable[Car]:
        raise NotImplementedError
