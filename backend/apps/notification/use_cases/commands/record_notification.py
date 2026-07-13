"""Record notification command."""

from backend.apps.notification.domain.models import Notification
from backend.apps.notification.domain.repository_interfaces import (
    NotificationRepositoryInterface,
)
from backend.shared.domain import UseCase


class RecordNotificationUseCase(UseCase):
    """Persist a notification that was triggered by a domain event."""

    def __init__(self, notification_repository: NotificationRepositoryInterface = None):
        if notification_repository is None:
            from backend.apps.notification.repositories.notification_repository import (
                NotificationRepository,
            )

            self.notification_repo = NotificationRepository()
        else:
            self.notification_repo = notification_repository

    def execute(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: int,
        message: str,
    ) -> dict:
        notification = Notification(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            message=message,
        )
        self.notification_repo.create(notification)
        return {
            "id": notification.id,
            "event_type": notification.event_type,
            "message": notification.message,
        }
