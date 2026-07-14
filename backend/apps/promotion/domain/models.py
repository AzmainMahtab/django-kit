"""Promotion domain models."""

from django.db import models


class Coupon(models.Model):
    """A coupon / discount code."""

    COUPON_ON = (
        ("product", "Product"),
        ("shipping", "Shipping"),
        ("combined", "Combined"),
    )
    COUPON_TYPE = (
        ("percentage", "Percentage"),
        ("fixed", "Fixed"),
    )

    coupon_code = models.CharField(max_length=50, unique=True)
    coupon_on = models.CharField(max_length=50, choices=COUPON_ON)
    coupon_type = models.CharField(max_length=50, choices=COUPON_TYPE)
    coupon_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_start_date = models.DateTimeField()
    coupon_expiry_date = models.DateTimeField()
    limit_per_user = models.IntegerField(default=-1)
    limit_per_coupon = models.IntegerField(default=-1)
    coupon_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "promotion_coupon"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.coupon_code


class CouponUsage(models.Model):
    """Tracks usage of a coupon on an order."""

    COUPON_USAGE_STATUS = (
        ("RESERVED", "Reserved"),
        ("CONFIRMED", "Confirmed"),
        ("REVERSED", "Reversed"),
    )

    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, related_name="usages"
    )
    user_id = models.IntegerField(db_index=True)
    order_id = models.IntegerField(unique=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=COUPON_USAGE_STATUS, default="RESERVED"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "promotion_couponusage"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.coupon.coupon_code} - {self.order_id}"
