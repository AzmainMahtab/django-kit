"""Django ORM implementation of the RBAC repository."""

from typing import Iterable

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.models import Permission, Role, RolePermission, UserRole
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface

User = get_user_model()


class RbacRepository(RbacRepositoryInterface):
    """Implements RbacRepositoryInterface using Django ORM."""

    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = "",
    ) -> Permission:
        return Permission.objects.create(
            name=name,
            resource=resource,
            action=action,
            description=description,
        )

    def get_permission_by_id(self, permission_id: int) -> Permission:
        return Permission.objects.get(pk=permission_id)

    def list_permissions(self) -> Iterable[Permission]:
        return Permission.objects.all().order_by("name")

    def create_role(self, name: str, description: str = "") -> Role:
        return Role.objects.create(name=name, description=description)

    def get_role_by_id(self, role_id: int) -> Role:
        return Role.objects.get(pk=role_id)

    def list_roles(self) -> Iterable[Role]:
        return Role.objects.all().order_by("name")

    def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        assigned_by_id: int | None = None,
    ) -> None:
        assigned_by = User.objects.get(pk=assigned_by_id) if assigned_by_id else None
        UserRole.objects.create(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
        )

    def revoke_role_from_user(self, user_id: int, role_id: int) -> None:
        UserRole.objects.filter(user_id=user_id, role_id=role_id).delete()

    def assign_permission_to_role(
        self,
        role_id: int,
        permission_id: int,
        assigned_by_id: int | None = None,
    ) -> None:
        assigned_by = User.objects.get(pk=assigned_by_id) if assigned_by_id else None
        RolePermission.objects.create(
            role_id=role_id,
            permission_id=permission_id,
            assigned_by=assigned_by,
        )

    def revoke_permission_from_role(self, role_id: int, permission_id: int) -> None:
        RolePermission.objects.filter(role_id=role_id, permission_id=permission_id).delete()

    def get_user_roles(self, user_id: int) -> Iterable[Role]:
        return Role.objects.filter(user_roles__user_id=user_id).order_by("name")

    def get_user_permissions(self, user_id: int) -> Iterable[Permission]:
        return (
            Permission.objects.filter(roles__user_roles__user_id=user_id)
            .distinct()
            .order_by("name")
        )

    def check_user_permission(self, user_id: int, permission_name: str) -> bool:
        return self.get_user_permissions(user_id).filter(name=permission_name).exists()

    def check_user_role(self, user_id: int, role_name: str) -> bool:
        return self.get_user_roles(user_id).filter(name=role_name).exists()

    def check_permission_on_role(self, role_id: int, permission_id: int) -> bool:
        return RolePermission.objects.filter(
            role_id=role_id,
            permission_id=permission_id,
        ).exists()
