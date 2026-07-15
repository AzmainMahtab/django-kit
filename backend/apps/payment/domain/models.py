"""Payment domain models."""

import uuid

from django.db import models


class Payment(models.Model):
    """A payment or refund transaction."""

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        CHEQUE = "CHEQUE", "Cheque"
        ONLINE = "ONLINE", "Online"
        POINTS = "POINTS", "Points"

    class PaymentType(models.TextChoices):
        REFUND = "REFUND", "Refund"
        PAYMENT = "PAYMENT", "Payment"

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.SUCCESS
    )
    method = models.CharField(
        max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CARD
    )
    type = models.CharField(
        max_length=10, choices=PaymentType.choices, default=PaymentType.PAYMENT
    )
    trans_id = models.CharField(max_length=255, null=True, blank=True)
    order_id = models.IntegerField(null=True, blank=True, db_index=True)
    card_number = models.CharField(max_length=50, null=True, blank=True)
    job_change_id = models.IntegerField(null=True, blank=True)
    transactions_history = models.JSONField(null=True, blank=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_payment"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment {self.amount} ({self.method})"


class PendingRefund(models.Model):
    """A refund pending processing."""

    class PendingRefundStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    order_id = models.IntegerField(db_index=True)
    payment_id = models.IntegerField(db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    card_number = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=PendingRefundStatus.choices,
        default=PendingRefundStatus.PENDING,
    )
    transaction_id = models.CharField(max_length=255)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    points = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_pendingrefund"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Pending Refund {self.amount}"
