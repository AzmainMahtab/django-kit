"""Create role command."""

from backend.apps.rbac.domain.events import RoleCreated
from backend.apps.rbac.domain.models import Role
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.event_bus import event_bus
from backend.shared.exceptions import BusinessValidationError


class CreateRoleUseCase(UseCase):
    """Create a new role and publish a domain event."""

    def __init__(self, rbac_repository: RbacRepositoryInterface = None):
        if rbac_repository is None:
            from backend.apps.rbac.repositories.rbac_repository import RbacRepository
            self.rbac_repo = RbacRepository()
        else:
            self.rbac_repo = rbac_repository

    def execute(self, name: str, description: str = "") -> Role:
        existing = [r for r in self.rbac_repo.list_roles() if r.name == name]
        if existing:
            raise BusinessValidationError(f"Role '{name}' already exists.")

        role = self.rbac_repo.create_role(name=name, description=description)

        event_bus.publish(
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
