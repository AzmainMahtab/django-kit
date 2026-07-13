"""List notifications query."""

from backend.apps.notification.domain.repository_interfaces import (
    NotificationRepositoryInterface,
)
from backend.shared.domain import UseCase


class ListNotificationsUseCase(UseCase):
    """Read recent notifications."""

    def __init__(self, notification_repository: NotificationRepositoryInterface = None):
        if notification_repository is None:
            from backend.apps.notification.repositories.notification_repository import (
                NotificationRepository,
            )

            self.notification_repo = NotificationRepository()
        else:
            self.notification_repo = notification_repository

    def execute(self, limit: int = 50) -> list[dict]:
        notifications = self.notification_repo.list_notifications()
        notifications = notifications[:limit]
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
