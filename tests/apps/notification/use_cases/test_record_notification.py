"""Tests for RecordNotificationUseCase."""

from backend.apps.notification.domain.models import Notification
from backend.apps.notification.use_cases.commands.record_notification import (
    RecordNotificationUseCase,
)


class MockNotificationRepository:
    def __init__(self):
        self.notifications = []

    def create(self, notification: Notification) -> Notification:
        notification.id = len(self.notifications) + 1
        self.notifications.append(notification)
        return notification


def test_record_notification():
    repo = MockNotificationRepository()
    use_case = RecordNotificationUseCase(notification_repository=repo)

    result = use_case.execute(
        event_type="ordering.job_status_changed",
        aggregate_type="job",
        aggregate_id=42,
        message="Job moved to PREPRESS",
    )

    assert result["event_type"] == "ordering.job_status_changed"
    assert result["message"] == "Job moved to PREPRESS"
    assert len(repo.notifications) == 1
