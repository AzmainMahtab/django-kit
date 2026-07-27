"""Public API for the notification module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.notification.use_cases.commands.record_notification import (
    RecordNotificationUseCase,
)
from backend.apps.notification.use_cases.queries.list_notifications import (
    ListNotificationsUseCase,
)
from backend.shared.event_bus import EventBus


class NotificationUseCases:
    """Facade that other modules use."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.commands = NotificationCommands(event_bus=event_bus)
        self.queries = NotificationQueries()

    def record_notification(self, **kwargs):
        return self.commands.record_notification.execute(**kwargs)

    def list_notifications(self, **kwargs):
        return self.queries.list_notifications.execute(**kwargs)


class NotificationCommands:
    def __init__(self, event_bus: EventBus) -> None:
        self.record_notification = RecordNotificationUseCase(event_bus=event_bus)


class NotificationQueries:
    def __init__(self):
        self.list_notifications = ListNotificationsUseCase()
