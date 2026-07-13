"""Base domain primitives."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_type: str
    aggregate_id: Any = None
    data: dict = field(default_factory=dict)


class UseCase:
    """Base class for all use cases."""

    def execute(self, **kwargs):
        """Every use case exposes exactly one entry point."""
        raise NotImplementedError
