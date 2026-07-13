"""Revoke role from user command."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.events import RoleRevoked
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.exceptions import BusinessValidationError, NotFoundError

User = get_user_model()


class RevokeRoleFromUserUseCase(UseCase):
    """Revoke a role from a user and publish a domain event."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(self, user_id: int, role_id: int) -> dict:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        try:
            role = self.rbac_repo.get_role_by_id(role_id)
        except Exception as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        if not self.rbac_repo.check_user_role(user_id, role.name):
            raise BusinessValidationError(
                f"Role '{role.name}' is not assigned to user {user_id}."
            )

        self.rbac_repo.revoke_role_from_user(user_id=user_id, role_id=role_id)

        event_bus.publish(
            RoleRevoked(
                aggregate_id=user_id,
                data={
                    "user_id": user_id,
                    "role_id": role_id,
                },
            )
        )

        return {"user_id": user_id, "role_id": role_id}
