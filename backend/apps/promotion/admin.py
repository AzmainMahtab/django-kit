"""Django admin configuration for promotion."""

from django.contrib import admin

from backend.apps.promotion.domain.models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "coupon_code",
        "coupon_on",
        "coupon_type",
        "coupon_value",
        "max_discount",
        "coupon_start_date",
        "coupon_expiry_date",
    )
    list_filter = ("coupon_on", "coupon_type")
    search_fields = ("coupon_code",)
    inlines = [CouponUsageInline]


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "order_id", "user_id", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("coupon__coupon_code", "order_id")
