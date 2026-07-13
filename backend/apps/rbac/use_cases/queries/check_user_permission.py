"""Check user permission query."""

from django.contrib.auth import get_user_model

from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError

User = get_user_model()


class CheckUserPermissionUseCase(UseCase):
    """Pure read: check whether a user has a specific effective permission."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(self, user_id: int, permission: str) -> dict:
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        return {
            "user_id": user_id,
            "permission": permission,
            "has_permission": self.rbac_repo.check_user_permission(user_id, permission),
        }
