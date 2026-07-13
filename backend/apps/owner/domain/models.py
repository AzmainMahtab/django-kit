"""Owner domain models."""

import uuid

from django.conf import settings
from django.db import models


class Owner(models.Model):
    """An owner of cars, linked to a User."""

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owner_profile",
        db_index=True,
    )
    address = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "owners"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Owner {self.uuid} (user {self.user_id})"
