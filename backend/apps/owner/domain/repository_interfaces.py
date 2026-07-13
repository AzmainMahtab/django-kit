"""Owner repository interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Iterable

from backend.apps.owner.domain.models import Owner


class OwnerRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, owner_id: int) -> Owner:
        """Return an owner by primary key or raise Owner.DoesNotExist."""
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Owner | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Owner | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, owner: Owner) -> Owner:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Iterable[Owner]:
        raise NotImplementedError
