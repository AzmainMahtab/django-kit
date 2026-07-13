"""Re-export car domain models for Django discovery."""

from backend.apps.car.domain.models import Car

__all__ = ["Car"]
