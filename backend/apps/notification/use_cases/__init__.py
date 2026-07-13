"""Public API for the notification module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.notification.use_cases.commands.record_notification import (
    RecordNotificationUseCase,
)
from backend.apps.notification.use_cases.queries.list_notifications import (
    ListNotificationsUseCase,
)


class NotificationUseCases:
    """Facade that other modules use."""

    def __init__(self):
        self.commands = NotificationCommands()
        self.queries = NotificationQueries()

    def record_notification(self, **kwargs):
        return self.commands.record_notification.execute(**kwargs)

    def list_notifications(self, **kwargs):
        return self.queries.list_notifications.execute(**kwargs)


class NotificationCommands:
    def __init__(self):
        self.record_notification = RecordNotificationUseCase()


class NotificationQueries:
    def __init__(self):
        self.list_notifications = ListNotificationsUseCase()
