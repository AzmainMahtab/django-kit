"""Get user permissions query."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError

User = get_user_model()


class GetUserPermissionsUseCase(UseCase):
    """Pure read: list effective permissions for a user via their roles."""

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

        permissions = self.rbac_repo.get_user_permissions(user_id)
        return [
            {
                "id": p.id,
                "name": p.name,
                "resource": p.resource,
                "action": p.action,
            }
            for p in permissions
        ]
