"""Car domain models."""

import uuid
from typing import cast

from django.db import models


class CarQuerySet(models.QuerySet):
    def by_owner(self, owner_id: int):
        return self.filter(owner_id=owner_id)

    def by_license_plate(self, license_plate: str):
        return self.filter(license_plate=license_plate)


class CarManager(models.Manager):
    def get_queryset(self):
        return CarQuerySet(self.model, using=self._db)

    def get_by_uuid(self, uuid: str) -> "Car | None":
        try:
            return cast("Car", self.get(uuid=uuid))
        except Car.DoesNotExist:
            return None

    def get_by_license_plate(self, license_plate: str) -> "Car | None":
        try:
            return cast("Car", self.get(license_plate=license_plate))
        except Car.DoesNotExist:
            return None

    def list_by_owner(self, owner_id: int):
        return self.get_queryset().by_owner(owner_id).order_by("-created_at")

    def list_all(self):
        return self.get_queryset().order_by("-created_at")


class Car(models.Model):
    """A car belonging to an Owner."""

    objects = CarManager()

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner_id = models.IntegerField(db_index=True)
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
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"
