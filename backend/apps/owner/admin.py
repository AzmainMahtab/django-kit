"""Django admin for owner models."""

from django.contrib import admin

from backend.apps.owner.domain.models import Owner


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "address", "date_of_birth", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "address")
    readonly_fields = ("uuid", "created_at", "updated_at")
