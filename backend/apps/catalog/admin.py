"""Django admin configuration for catalog."""

from django.contrib import admin

from backend.apps.catalog.domain.models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product_code",
        "category",
        "min_price",
        "max_price",
        "is_active",
        "on_draft",
        "created_at",
    )
    list_filter = ("is_active", "on_draft", "category", "product_type")
    search_fields = ("name", "product_code")
    autocomplete_fields = ("category",)
