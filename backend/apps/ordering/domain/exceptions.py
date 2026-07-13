"""Ordering domain exceptions."""

from backend.shared.exceptions import NotFoundError


class OrderNotFoundError(NotFoundError):
    """Raised when an order cannot be found."""


class JobNotFoundError(NotFoundError):
    """Raised when a job cannot be found."""
