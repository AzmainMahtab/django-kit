"""Get user roles query."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError

User = get_user_model()


class GetUserRolesUseCase(UseCase):
    """Pure read: list roles assigned to a user."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(self, user_id: int) -> list[dict]:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        roles = self.rbac_repo.get_user_roles(user_id)
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
            }
            for r in roles
        ]
