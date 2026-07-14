"""Django admin for the event outbox infrastructure."""

from django.contrib import admin

from backend.apps.event_outbox.models import DeadLetterEvent, EventOutbox, EventStore


@admin.register(EventOutbox)
class EventOutboxAdmin(admin.ModelAdmin):
    list_display = ("event_class_path", "created_at", "published_at", "attempts")
    list_filter = ("event_class_path", "published_at")
    search_fields = ("event_class_path", "payload")
    readonly_fields = ("id", "created_at")


@admin.register(EventStore)
class EventStoreAdmin(admin.ModelAdmin):
    list_display = ("event_type", "event_class_path", "aggregate_id", "published_at")
    list_filter = ("event_type", "event_class_path")
    search_fields = ("event_class_path", "aggregate_id", "correlation_id")
    readonly_fields = ("id", "published_at")


@admin.register(DeadLetterEvent)
class DeadLetterEventAdmin(admin.ModelAdmin):
    list_display = ("event_class_path", "attempts", "created_at", "resolved_at")
    list_filter = ("event_class_path", "resolved_at")
    search_fields = ("event_class_path", "error_message")
    readonly_fields = ("id", "created_at")
