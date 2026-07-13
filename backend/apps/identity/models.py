"""Re-export identity domain models so Django can discover them."""

from backend.apps.identity.domain.models import User

__all__ = ["User"]
