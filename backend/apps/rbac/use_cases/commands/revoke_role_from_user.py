"""Revoke role from user command."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.events import RoleRevoked
from backend.apps.rbac.domain.models import Role, UserRole
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError, NotFoundError

User = get_user_model()


class RevokeRoleFromUserUseCase(UseCase):
    """Revoke a role from a user and publish a domain event."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(self, user_id: int, role_id: int) -> dict:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        if not UserRole.objects.filter(user_id=user_id, role_id=role_id).exists():
            raise BusinessValidationError(
                f"Role '{role.name}' is not assigned to user {user_id}."
            )

        UserRole.objects.filter(user_id=user_id, role_id=role_id).delete()

        self.event_bus.publish(
            RoleRevoked(
                aggregate_id=user_id,
                data={
                    "user_id": user_id,
                    "role_id": role_id,
                },
            )
        )

        return {"user_id": user_id, "role_id": role_id}
