"""Event outbox, event store, and dead-letter models.

These models make the event bus durable, auditable, and fault-tolerant:

- ``EventOutbox``: events staged inside the same database transaction as the
  business write. A relay process publishes them after the transaction commits.
- ``EventStore``: append-only log of every published event for debugging,
  replay, and compliance.
- ``DeadLetterEvent``: events that failed processing after all retries, kept
  for inspection and manual replay.
"""

import uuid

from django.db import models


class EventOutbox(models.Model):
    """A staged event waiting to be published after the current DB transaction commits."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_class_path = models.CharField(max_length=255, db_index=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "event_outbox"
        ordering = ["created_at"]
        verbose_name_plural = "event outbox entries"

    def __str__(self) -> str:
        return f"{self.event_class_path} ({'published' if self.published_at else 'pending'})"


class EventStore(models.Model):
    """Append-only audit log of published domain events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=128, db_index=True)
    event_class_path = models.CharField(max_length=255, db_index=True)
    aggregate_id = models.CharField(max_length=64, blank=True, db_index=True)
    payload = models.JSONField()
    correlation_id = models.CharField(max_length=64, blank=True, db_index=True)
    published_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "event_store"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return f"{self.event_type} at {self.published_at}"


class DeadLetterEvent(models.Model):
    """Events that could not be processed after all retries."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_class_path = models.CharField(max_length=255, db_index=True)
    payload = models.JSONField()
    error_message = models.TextField()
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "event_dead_letter"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_class_path} failed {self.attempts} times"
