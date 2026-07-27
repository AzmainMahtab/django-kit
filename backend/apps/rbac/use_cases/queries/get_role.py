"""Get role query."""

from backend.apps.rbac.domain.models import Role
from backend.shared.domain import UseCase
from backend.shared.exceptions import NotFoundError


class GetRoleUseCase(UseCase):
    """Pure read: fetch a role by id."""

    def execute(self, role_id: int) -> dict:
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist as exc:
            raise NotFoundError(f"Role with id {role_id} not found.") from exc

        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
        }
