"""Django admin configuration for notification."""

from django.contrib import admin

from backend.apps.notification.domain.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("event_type", "aggregate_type", "aggregate_id", "message", "created_at")
    list_filter = ("event_type", "aggregate_type")
    search_fields = ("message",)
