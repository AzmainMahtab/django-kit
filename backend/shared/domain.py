"""Base domain primitives."""

from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar


@dataclass
class DomainEvent:
    """Base class for all domain events.

    Subclasses declare a class-level ``event_type`` so the event bus can
    route handlers without relying on string constants at every call site.
    """

    event_type: ClassVar[str] = "base.domain_event"
    aggregate_id: Any = None
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize the event instance for durable transport (e.g. Celery)."""
        return asdict(self)


class UseCase:
    """Base class for all use cases."""

    def execute(self, **kwargs):
        """Every use case exposes exactly one entry point."""
        raise NotImplementedError
