"""Get user roles query."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.models import Role
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError

User = get_user_model()


class GetUserRolesUseCase(UseCase):
    """Pure read: list roles assigned to a user."""

    def execute(self, user_id: int) -> list[dict]:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        roles = Role.objects.filter(user_roles__user_id=user_id).order_by("name")
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
            }
            for r in roles
        ]
