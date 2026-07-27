"""Record notification command."""

from backend.apps.notification.domain.models import Notification
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus


class RecordNotificationUseCase(UseCase):
    """Persist a notification that was triggered by a domain event."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: int,
        message: str,
    ) -> dict:
        notification = Notification.objects.create(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            message=message,
        )
        return {
            "id": notification.id,
            "event_type": notification.event_type,
            "message": notification.message,
        }
