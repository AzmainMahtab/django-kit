"""Identity repository interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Iterable

from backend.apps.identity.domain.models import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def list_users(self, filters: dict = None) -> Iterable[User]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **kwargs) -> User:
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User, update_fields: list[str] = None) -> User:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user: User) -> None:
        raise NotImplementedError
