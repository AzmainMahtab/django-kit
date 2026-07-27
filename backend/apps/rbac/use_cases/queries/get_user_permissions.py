"""Get user permissions query."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.models import Permission
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError

User = get_user_model()


class GetUserPermissionsUseCase(UseCase):
    """Pure read: list effective permissions for a user via their roles."""

    def execute(self, user_id: int) -> list[dict]:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        permissions = (
            Permission.objects.filter(roles__user_roles__user_id=user_id)
            .distinct()
            .order_by("name")
        )
        return [
            {
                "id": p.id,
                "name": p.name,
                "resource": p.resource,
                "action": p.action,
            }
            for p in permissions
        ]
