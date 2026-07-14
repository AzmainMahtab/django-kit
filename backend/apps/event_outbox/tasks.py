"""Celery tasks for the event outbox relay and dead-letter handling."""

import logging
from datetime import UTC, datetime, timedelta

from celery import shared_task
from django.db import transaction
from django.utils.module_loading import import_string

from backend.apps.event_outbox.models import DeadLetterEvent, EventOutbox, EventStore
from backend.shared.domain import DomainEvent
from backend.shared.event_bus import EventBus

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def relay_outbox_event(self, outbox_id: str):
    """Publish a single outbox entry to the in-process event bus.

    On failure the task retries with Celery's backoff. After max retries the
    event is moved to the dead-letter store.
    """
    try:
        outbox = EventOutbox.objects.get(pk=outbox_id, published_at__isnull=True)
    except EventOutbox.DoesNotExist:
        logger.warning("Outbox entry %s not found or already published", outbox_id)
        return

    try:
        event_cls = import_string(outbox.event_class_path)
        event = event_cls(**outbox.payload)
    except Exception as exc:
        logger.exception("Cannot deserialize outbox event %s", outbox_id)
        _move_to_dead_letter(outbox, exc)
        return

    bus = EventBus()
    try:
        bus.publish(event)
    except Exception as exc:
        logger.exception("Failed to publish outbox event %s", outbox_id)
        outbox.attempts += 1
        outbox.save(update_fields=["attempts"])
        raise self.retry(exc=exc)

    with transaction.atomic():
        outbox.published_at = datetime.now(UTC)
        outbox.save(update_fields=["published_at"])
        EventStore.objects.create(
            event_type=event.event_type,
            event_class_path=outbox.event_class_path,
            aggregate_id=str(getattr(event, "aggregate_id", "")),
            payload=outbox.payload,
        )

    logger.info("Relayed outbox event %s", outbox_id)


@shared_task
def relay_pending_outbox_events():
    """Celery Beat task: relay all pending outbox entries.

    Run this every few seconds via django-celery-beat.
    """
    pending_ids = list(
        EventOutbox.objects.filter(published_at__isnull=True)
        .order_by("created_at")
        .values_list("id", flat=True)[:1000]
    )

    for outbox_id in pending_ids:
        relay_outbox_event.delay(str(outbox_id))

    logger.info("Relayed %d pending outbox entries", len(pending_ids))


@shared_task
def archive_processed_outbox_events(older_than_minutes: int = 60):
    """Clean up outbox entries that were published a while ago."""
    cutoff = datetime.now(UTC) - timedelta(minutes=older_than_minutes)
    deleted, _ = EventOutbox.objects.filter(published_at__lt=cutoff).delete()
    logger.info("Archived %d processed outbox entries", deleted)


def _move_to_dead_letter(outbox: EventOutbox, exc: Exception) -> None:
    """Move an unprocessable outbox entry to the dead-letter store."""
    DeadLetterEvent.objects.create(
        event_class_path=outbox.event_class_path,
        payload=outbox.payload,
        error_message=str(exc),
        attempts=outbox.attempts,
    )
    outbox.published_at = datetime.now(UTC)
    outbox.save(update_fields=["published_at"])
