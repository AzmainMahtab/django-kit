"""Check user permission query."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.models import Role
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError

User = get_user_model()


class CheckUserPermissionUseCase(UseCase):
    """Pure read: check whether a user has a specific effective permission."""

    def execute(self, user_id: int, permission: str) -> dict:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        return {
            "user_id": user_id,
            "permission": permission,
            "has_permission": Role.objects.filter(
                user_roles__user_id=user_id,
                role_permissions__permission__name=permission,
            ).exists(),
        }
