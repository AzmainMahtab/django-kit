"""Django admin for car models."""

from django.contrib import admin

from backend.apps.car.domain.models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("uuid", "owner_id", "make", "model", "year", "license_plate", "created_at")
    list_filter = ("make", "year", "created_at")
    search_fields = ("make", "model", "license_plate")
    readonly_fields = ("uuid", "created_at", "updated_at")
