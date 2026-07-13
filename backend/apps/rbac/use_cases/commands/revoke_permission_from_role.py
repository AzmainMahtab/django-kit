"""Revoke permission from role command."""

from backend.apps.rbac.domain.events import PermissionRevokedFromRole
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.exceptions import BusinessValidationError, NotFoundError


class RevokePermissionFromRoleUseCase(UseCase):
    """Revoke a permission from a role and publish a domain event."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(self, role_id: int, permission_id: int) -> dict:
        try:
            role = self.rbac_repo.get_role_by_id(role_id)
        except Exception as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        try:
            permission = self.rbac_repo.get_permission_by_id(permission_id)
        except Exception as exc:
            raise NotFoundError(f"Permission with id {permission_id} not found.") from exc

        has_permission = self.rbac_repo.check_permission_on_role(
            role_id=role_id,
            permission_id=permission_id,
        )
        if not has_permission:
            raise BusinessValidationError(
                f"Permission '{permission.name}' is not assigned to role '{role.name}'."
            )

        self.rbac_repo.revoke_permission_from_role(role_id=role_id, permission_id=permission_id)

        event_bus.publish(
            PermissionRevokedFromRole(
                aggregate_id=role_id,
                data={
                    "role_id": role_id,
                    "permission_id": permission_id,
                },
            )
        )

        return {"role_id": role_id, "permission_id": permission_id}
