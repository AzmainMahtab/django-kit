"""Django admin configuration for payment."""

from django.contrib import admin

from backend.apps.payment.domain.models import Payment, PendingRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_id",
        "amount",
        "status",
        "method",
        "type",
        "trans_id",
        "created_at",
    )
    list_filter = ("status", "method", "type")
    search_fields = ("trans_id", "order_id")


@admin.register(PendingRefund)
class PendingRefundAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_id",
        "payment_id",
        "amount",
        "status",
        "transaction_id",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("transaction_id", "order_id")
