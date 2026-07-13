"""Ordering domain models."""

from django.db import models


class Order(models.Model):
    """A customer order."""

    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    user_id = models.IntegerField(db_index=True)
    status = models.CharField(max_length=32, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ordering_order"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.order_number


class Job(models.Model):
    """A production job belonging to an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="jobs",
        db_index=True,
    )
    job_id = models.CharField(max_length=32, unique=True, db_index=True)
    job_status = models.CharField(max_length=32, default="PENDING")
    file_editable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ordering_job"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.job_id
