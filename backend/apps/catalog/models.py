"""Re-export domain models so Django discovers them."""

from backend.apps.catalog.domain.models import Product, ProductCategory  # noqa: F401
