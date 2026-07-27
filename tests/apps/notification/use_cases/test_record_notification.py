"""Tests for RecordNotificationUseCase."""

import pytest

from backend.apps.notification.domain.models import Notification
from backend.apps.notification.use_cases.commands.record_notification import (
    RecordNotificationUseCase,
)
from backend.shared.event_bus import EventBus

pytestmark = pytest.mark.django_db


def test_record_notification():
    bus = EventBus()
    use_case = RecordNotificationUseCase(event_bus=bus)

    result = use_case.execute(
        event_type="ordering.job_status_changed",
        aggregate_type="job",
        aggregate_id=42,
        message="Job moved to PREPRESS",
    )

    assert result["event_type"] == "ordering.job_status_changed"
    assert result["message"] == "Job moved to PREPRESS"
    assert Notification.objects.count() == 1
