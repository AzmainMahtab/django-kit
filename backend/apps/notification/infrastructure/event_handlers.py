"""Notification event handlers."""

from backend.apps.notification.use_cases import NotificationUseCases
from backend.shared.events import JobStatusChanged


def on_job_status_changed(
    notification_facade: NotificationUseCases,
    event: JobStatusChanged,
) -> None:
    """Record a notification when a job status changes."""
    data = event.data
    message = (
        f"Job {data.get('job_uuid')} moved from {data.get('old_status')} "
        f"to {data.get('new_status')}"
    )

    notification_facade.record_notification(
        event_type=event.event_type,
        aggregate_type="job",
        aggregate_id=event.aggregate_id,
        message=message,
    )
