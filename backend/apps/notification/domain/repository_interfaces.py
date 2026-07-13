"""Notification repository ports."""

from typing import Protocol

from backend.apps.notification.domain.models import Notification


class NotificationRepositoryInterface(Protocol):
    """Port for notification persistence."""

    def create(self, notification: Notification) -> Notification: ...

    def list_notifications(self, filters: dict = None) -> list[Notification]: ...
