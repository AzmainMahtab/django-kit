"""Notification domain models."""

from django.db import models


class Notification(models.Model):
    """A notification triggered by a domain event."""

    event_type = models.CharField(max_length=64, db_index=True)
    aggregate_type = models.CharField(max_length=32, default="")
    aggregate_id = models.IntegerField(null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification_notification"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type}: {self.message[:50]}"
