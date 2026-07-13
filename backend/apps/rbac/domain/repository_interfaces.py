"""RBAC repository interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Iterable

from backend.apps.rbac.domain.models import Permission, Role


class RbacRepositoryInterface(ABC):
    @abstractmethod
    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = "",
    ) -> Permission:
        raise NotImplementedError

    @abstractmethod
    def get_permission_by_id(self, permission_id: int) -> Permission:
        raise NotImplementedError

    @abstractmethod
    def list_permissions(self) -> Iterable[Permission]:
        raise NotImplementedError

    @abstractmethod
    def create_role(self, name: str, description: str = "") -> Role:
        raise NotImplementedError

    @abstractmethod
    def get_role_by_id(self, role_id: int) -> Role:
        raise NotImplementedError

    @abstractmethod
    def list_roles(self) -> Iterable[Role]:
        raise NotImplementedError

    @abstractmethod
    def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        assigned_by_id: int | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def revoke_role_from_user(self, user_id: int, role_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def assign_permission_to_role(
        self,
        role_id: int,
        permission_id: int,
        assigned_by_id: int | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def revoke_permission_from_role(self, role_id: int, permission_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_user_roles(self, user_id: int) -> Iterable[Role]:
        raise NotImplementedError

    @abstractmethod
    def get_user_permissions(self, user_id: int) -> Iterable[Permission]:
        raise NotImplementedError

    @abstractmethod
    def check_user_permission(self, user_id: int, permission_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def check_user_role(self, user_id: int, role_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def check_permission_on_role(self, role_id: int, permission_id: int) -> bool:
        raise NotImplementedError
