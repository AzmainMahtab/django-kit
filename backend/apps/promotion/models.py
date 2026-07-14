"""Re-export domain models so Django discovers them."""

from backend.apps.promotion.domain.models import Coupon, CouponUsage  # noqa: F401
