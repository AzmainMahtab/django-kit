"""Catalog domain models."""

from django.db import models


class ProductCategory(models.Model):
    """Product category."""

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_productcategory"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """A product in the catalog."""

    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_code = models.CharField(max_length=255, unique=True, db_index=True)
    created_by_id = models.IntegerField(null=True, blank=True, db_index=True)
    product_type = models.CharField(max_length=255, default="OFFSET")
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sqr_ft_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shop_rate_per_hr = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    is_active = models.BooleanField(default=False)
    on_draft = models.BooleanField(default=True)
    base_turnaround = models.IntegerField(default=2)
    combined_shipping = models.BooleanField(default=False)
    ordering = models.IntegerField(default=1)
    show_faq = models.BooleanField(default=True)
    shipping_type = models.CharField(max_length=10, default="DEFAULT")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_product"
        ordering = ["-is_active", "-on_draft", "ordering", "-created_at"]

    def __str__(self) -> str:
        return self.name
