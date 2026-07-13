"""Get role query."""

from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError


class GetRoleUseCase(UseCase):
    """Pure read: fetch a role by id."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(self, role_id: int) -> dict:
        try:
            role = self.rbac_repo.get_role_by_id(role_id)
        except Exception as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
        }
