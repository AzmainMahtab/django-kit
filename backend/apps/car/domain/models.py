"""Car domain models."""

import uuid

from django.db import models


class Car(models.Model):
    """A car belonging to an Owner."""

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(
        "owner.Owner",
        on_delete=models.CASCADE,
        related_name="cars",
        db_index=True,
    )
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    color = models.CharField(max_length=30)
    license_plate = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cars"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"
