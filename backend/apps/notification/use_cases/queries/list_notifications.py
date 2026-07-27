"""List notifications query."""

from backend.apps.notification.domain.models import Notification
from backend.shared.domain import UseCase


class ListNotificationsUseCase(UseCase):
    """Read recent notifications."""

    def execute(self, limit: int = 50) -> list[dict]:
        notifications = Notification.objects.order_by("-created_at")[:limit]
        return [
            {
                "id": n.id,
                "event_type": n.event_type,
                "aggregate_type": n.aggregate_type,
                "aggregate_id": n.aggregate_id,
                "message": n.message,
                "created_at": n.created_at,
            }
            for n in notifications
        ]
