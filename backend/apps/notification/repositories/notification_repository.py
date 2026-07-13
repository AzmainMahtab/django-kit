"""Django ORM implementation of notification repository."""

from backend.apps.notification.domain.models import Notification


class NotificationRepository:
    """Implements NotificationRepositoryInterface using Django ORM."""

    def create(self, notification: Notification) -> Notification:
        notification.save()
        return notification

    def list_notifications(self, filters: dict = None) -> list[Notification]:
        qs = Notification.objects.order_by("-created_at")
        if filters:
            qs = qs.filter(**filters)
        return list(qs)
