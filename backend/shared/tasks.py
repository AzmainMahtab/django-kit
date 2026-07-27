"""Shared Celery tasks used by the event bus and other infrastructure."""

import logging

from celery import shared_task
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def dispatch_domain_event(self, event_class_path: str, payload: dict):
    """Dispatch a domain event to all subscribed handlers asynchronously.

    The event is reconstructed from its class path and payload, then published
    to the in-process event bus. On failure the task retries with Celery's
    backoff; after max retries it is routed to the dead-letter store by the
    broker or by manual inspection.
    """
    from backend.shared.event_bus import EventBus

    try:
        event_cls = import_string(event_class_path)
        event = event_cls(**payload)
    except Exception as exc:
        logger.exception("Cannot deserialize event %s", event_class_path)
        # Do not retry deserialization errors; they are permanent.
        _record_dead_letter(event_class_path, payload, exc)
        return

    try:
        event_bus = EventBus()
        event_bus.publish(event)
    except Exception as exc:
        logger.exception("Error dispatching event %s", event_class_path)
        raise self.retry(exc=exc) from exc


def _record_dead_letter(event_class_path: str, payload: dict, exc: Exception) -> None:
    """Persist an unprocessable event to the dead-letter store."""
    from backend.apps.event_outbox.models import DeadLetterEvent

    DeadLetterEvent.objects.create(
        event_class_path=event_class_path,
        payload=payload,
        error_message=str(exc),
    )
