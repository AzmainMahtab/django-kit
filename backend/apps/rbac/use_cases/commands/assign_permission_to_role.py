"""Assign permission to role command."""

from backend.apps.rbac.domain.events import PermissionAssignedToRole
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.exceptions import BusinessValidationError, NotFoundError


class AssignPermissionToRoleUseCase(UseCase):
    """Assign a permission to a role and publish a domain event."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(
        self,
        role_id: int,
        permission_id: int,
        assigned_by_id: int | None = None,
    ) -> dict:
        try:
            role = self.rbac_repo.get_role_by_id(role_id)
        except Exception as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        try:
            permission = self.rbac_repo.get_permission_by_id(permission_id)
        except Exception as exc:
            raise NotFoundError(f"Permission with id {permission_id} not found.") from exc

        if self.rbac_repo.check_permission_on_role(role_id=role_id, permission_id=permission_id):
            raise BusinessValidationError(
                f"Permission '{permission.name}' is already assigned to role '{role.name}'."
            )

        self.rbac_repo.assign_permission_to_role(
            role_id=role_id,
            permission_id=permission_id,
            assigned_by_id=assigned_by_id,
        )

        event_bus.publish(
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
