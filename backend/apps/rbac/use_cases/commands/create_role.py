"""Create role command."""

from backend.apps.rbac.domain.events import RoleCreated
from backend.apps.rbac.domain.models import Role
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError


class CreateRoleUseCase(UseCase):
    """Create a new role and publish a domain event."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(self, name: str, description: str = "") -> Role:
        if Role.objects.filter(name=name).exists():
            raise BusinessValidationError(f"Role '{name}' already exists.")

        role = Role.objects.create(name=name, description=description)

        self.event_bus.publish(
            RoleCreated(
                aggregate_id=role.id,
                data={
                    "role_id": role.id,
                    "name": role.name,
                    "description": role.description,
                },
            )
        )

        return role
