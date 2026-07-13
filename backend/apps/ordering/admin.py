"""Django admin configuration for ordering."""

from django.contrib import admin

from backend.apps.ordering.domain.models import Job, Order


class JobInline(admin.TabularInline):
    model = Job
    extra = 0
    readonly_fields = ("job_id", "job_status", "file_editable")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user_id", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("order_number",)
    inlines = [JobInline]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("job_id", "order", "job_status", "file_editable", "updated_at")
    list_filter = ("job_status", "file_editable")
    search_fields = ("job_id", "order__order_number")
