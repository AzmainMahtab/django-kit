"""Django admin configuration for ordering."""

from django.contrib import admin

from backend.apps.ordering.domain.models import Job, JobMemo, Order


class JobInline(admin.TabularInline):
    model = Job
    extra = 0
    readonly_fields = (
        "job_id",
        "job_status",
        "file_editable",
        "product_id",
        "quantity",
        "price",
    )


class JobMemoInline(admin.TabularInline):
    model = JobMemo
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user_id",
        "status",
        "total_price",
        "final_price",
        "payment_status",
        "created_at",
    )
    list_filter = ("status", "payment_status")
    search_fields = ("order_number",)
    inlines = [JobInline]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "job_id",
        "order",
        "job_status",
        "product_id",
        "quantity",
        "price",
        "file_editable",
        "updated_at",
    )
    list_filter = ("job_status", "file_editable")
    search_fields = ("job_id", "order__order_number")
    inlines = [JobMemoInline]


@admin.register(JobMemo)
class JobMemoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "status",
        "adjustment_type",
        "total_adjustment",
        "created_at",
    )
    list_filter = ("status", "adjustment_type")
