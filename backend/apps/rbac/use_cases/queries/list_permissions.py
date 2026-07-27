"""List permissions query."""

from backend.apps.rbac.domain.models import Permission
from backend.shared.domain import UseCase


class ListPermissionsUseCase(UseCase):
    """Pure read: list all permissions."""

    def execute(self) -> list[dict]:
        permissions = Permission.objects.all().order_by("name")
        return [
            {
                "id": p.id,
                "name": p.name,
                "resource": p.resource,
                "action": p.action,
                "description": p.description,
            }
            for p in permissions
        ]
