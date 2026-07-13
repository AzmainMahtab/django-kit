"""Create permission command."""

from backend.apps.rbac.domain.events import PermissionCreated
from backend.apps.rbac.domain.models import Permission
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.exceptions import BusinessValidationError


class CreatePermissionUseCase(UseCase):
    """Create a new permission and publish a domain event."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = "",
    ) -> Permission:
        existing = [p for p in self.rbac_repo.list_permissions() if p.name == name]
        if existing:
            raise BusinessValidationError(f"Permission '{name}' already exists.")

        permission = self.rbac_repo.create_permission(
            name=name,
            resource=resource,
            action=action,
            description=description,
        )

        event_bus.publish(
            PermissionCreated(
                aggregate_id=permission.id,
                data={
                    "permission_id": permission.id,
                    "name": permission.name,
                    "resource": permission.resource,
                    "action": permission.action,
                },
            )
        )

        return permission
