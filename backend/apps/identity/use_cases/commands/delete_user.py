"""Delete user command."""

from backend.apps.identity.domain.events import UserDeleted
from backend.apps.identity.domain.models import User
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import NotFoundError


class DeleteUserUseCase(UseCase):
    """Delete a user."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(self, user_id: int) -> None:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise NotFoundError(f"User with id {user_id} not found.") from exc

        user.delete()

        self.event_bus.publish(
            UserDeleted(
                aggregate_id=user_id,
                data={"user_id": user_id},
            )
        )
