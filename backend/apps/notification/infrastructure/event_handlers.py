"""Notification event handlers."""

from backend.apps.ordering.domain.events import JobStatusChanged
from backend.apps.notification.use_cases import NotificationUseCases
from backend.shared.event_bus import event_bus


def on_job_status_changed(event: JobStatusChanged) -> None:
    """Record a notification when a job status changes."""
    data = event.data
    message = (
        f"Job {data.get('job_uuid')} moved from {data.get('old_status')} "
        f"to {data.get('new_status')}"
    )

    NotificationUseCases().record_notification(
        event_type=event.event_type,
        aggregate_type="job",
        aggregate_id=event.aggregate_id,
        message=message,
    )


def register_notification_handlers() -> None:
    event_bus.subscribe(JobStatusChanged.event_type, on_job_status_changed)
