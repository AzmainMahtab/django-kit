"""Create owner command."""

from datetime import date

from backend.apps.owner.domain.events import OwnerCreated
from backend.apps.owner.domain.exceptions import OwnerAlreadyExistsError
from backend.apps.owner.domain.models import Owner
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus


class CreateOwnerUseCase(UseCase):
    """Create a new owner profile for a user."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(
        self,
        user_id: int,
        address: str,
        date_of_birth: date | None = None,
    ) -> Owner:
        if Owner.objects.get_by_user_id(user_id):
            raise OwnerAlreadyExistsError(f"Owner for user {user_id} already exists.")

        owner = Owner.objects.create(
            user_id=user_id,
            address=address,
            date_of_birth=date_of_birth,
        )
        self.event_bus.publish(
            OwnerCreated(
                aggregate_id=owner.id,
                data={"owner_id": owner.id, "user_id": owner.user_id},
            )
        )
        return owner
