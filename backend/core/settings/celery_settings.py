"""Celery settings."""

import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    "relay-pending-outbox-events": {
        "task": "backend.apps.event_outbox.tasks.relay_pending_outbox_events",
        "schedule": 10.0,  # seconds
    },
    "archive-processed-outbox-events": {
        "task": "backend.apps.event_outbox.tasks.archive_processed_outbox_events",
        "schedule": 3600.0,  # seconds
    },
}
