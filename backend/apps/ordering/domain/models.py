"""Ordering domain models."""

from django.db import models


class Order(models.Model):
    """A customer order."""

    PAYMENT_STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("PAID", "PAID"),
        ("PARTIALLY_PAID", "PARTIALLY PAID"),
    )

    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    user_id = models.IntegerField(db_index=True)
    status = models.CharField(max_length=32, default="PENDING")

    # Financial fields from Elite4Print
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=32, choices=PAYMENT_STATUS_CHOICES, default="PENDING", db_index=True
    )
    extra_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_additional_payment_paid = models.BooleanField(default=False)
    original_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points_used = models.IntegerField(default=0)
    total_adjustment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_ref = models.JSONField(null=True, blank=True, default=dict)

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

    # Production fields from Elite4Print
    job_name = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.CharField(max_length=40, db_index=True, default="")
    process_status = models.CharField(max_length=5, blank=True, null=True)
    product_id = models.IntegerField(null=True, blank=True, db_index=True)
    item_code = models.CharField(max_length=255, blank=True, null=True)
    paper = models.CharField(max_length=150, default="No Paper")
    size = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    coating = models.CharField(max_length=150, default="No Coating")
    color = models.CharField(max_length=150, default="No Color")
    trim_size = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    turnaround = models.CharField(max_length=50, default="2 Business days")
    turnaround_day = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    cut_off_time = models.TimeField(null=True, blank=True)
    shipping_editable = models.BooleanField(default=True)
    pickup_location = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ordering_job"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.job_id


class JobMemo(models.Model):
    """A memo / adjustment attached to a job."""

    class MemoStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    class AdjustmentType(models.TextChoices):
        ADDITIONAL = "ADDITIONAL", "Additional Payment"
        REFUND = "REFUND", "Refund"
        NONE = "NONE", "No Adjustment"

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="memos"
    )
    note = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10, choices=MemoStatus.choices, default=MemoStatus.PENDING
    )
    printing_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adjustment_type = models.CharField(
        max_length=15,
        choices=AdjustmentType.choices,
        default=AdjustmentType.NONE,
    )
    total_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ordering_jobmemo"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Memo {self.id}"
