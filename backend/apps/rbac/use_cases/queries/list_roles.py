"""List roles query."""

from backend.apps.rbac.domain.models import Role
from backend.shared.domain import UseCase


class ListRolesUseCase(UseCase):
    """Pure read: list all roles."""

    def execute(self) -> list[dict]:
        roles = Role.objects.all().order_by("name")
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
            }
            for r in roles
        ]
