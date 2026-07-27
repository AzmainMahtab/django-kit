"""Owner domain models."""

import uuid
from typing import cast

from django.db import models


class OwnerManager(models.Manager):
    def get_by_uuid(self, uuid: str) -> "Owner | None":
        try:
            return cast("Owner", self.get(uuid=uuid))
        except Owner.DoesNotExist:
            return None

    def get_by_user_id(self, user_id: int) -> "Owner | None":
        try:
            return cast("Owner", self.get(user_id=user_id))
        except Owner.DoesNotExist:
            return None


class Owner(models.Model):
    """An owner of cars, linked to a User by ID only."""

    objects = OwnerManager()

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user_id = models.IntegerField(unique=True, db_index=True)
    address = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "owners"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Owner {self.uuid} (user {self.user_id})"

    @property
    def user(self):
        """Convenience accessor for admin / debugging.

        This is a soft reference; the owner module does not own the User model.
        """
        from django.contrib.auth import get_user_model

        return get_user_model().objects.get(pk=self.user_id)
