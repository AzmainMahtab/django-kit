"""Assign permission to role command."""

from backend.apps.rbac.domain.events import PermissionAssignedToRole
from backend.apps.rbac.domain.models import Permission, Role, RolePermission
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError, NotFoundError


class AssignPermissionToRoleUseCase(UseCase):
    """Assign a permission to a role and publish a domain event."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(
        self,
        role_id: int,
        permission_id: int,
        assigned_by_id: int | None = None,
    ) -> dict:
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        try:
            permission = Permission.objects.get(pk=permission_id)
        except Permission.DoesNotExist as exc:
            raise NotFoundError(f"Permission with id {permission_id} not found.") from exc

        if RolePermission.objects.filter(role_id=role_id, permission_id=permission_id).exists():
            raise BusinessValidationError(
                f"Permission '{permission.name}' is already assigned to role '{role.name}'."
            )

        RolePermission.objects.create(
            role_id=role_id,
            permission_id=permission_id,
            assigned_by_id=assigned_by_id,
        )

        self.event_bus.publish(
            PermissionAssignedToRole(
                aggregate_id=role_id,
                data={
                    "role_id": role_id,
                    "permission_id": permission_id,
                    "assigned_by_id": assigned_by_id,
                },
            )
        )

        return {"role_id": role_id, "permission_id": permission_id}
