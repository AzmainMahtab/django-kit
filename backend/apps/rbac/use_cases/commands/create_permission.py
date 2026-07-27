"""Create permission command."""

from backend.apps.rbac.domain.events import PermissionCreated
from backend.apps.rbac.domain.models import Permission
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError


class CreatePermissionUseCase(UseCase):
    """Create a new permission and publish a domain event."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = "",
    ) -> Permission:
        if Permission.objects.filter(name=name).exists():
            raise BusinessValidationError(f"Permission '{name}' already exists.")

        permission = Permission.objects.create(
            name=name,
            resource=resource,
            action=action,
            description=description,
        )

        self.event_bus.publish(
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
