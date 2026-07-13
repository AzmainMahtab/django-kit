"""In-process domain event bus — replaces Django signals."""

import logging
from collections import defaultdict
from typing import Callable

from backend.shared.domain import DomainEvent

logger = logging.getLogger(__name__)


class DomainEventBus:
    """
    In-process event bus. Replaces ALL Django signals for cross-module communication.

    Key differences from Django signals:
    - Explicit subscriptions in apps.py (not scattered in signals.py)
    - Testable: handlers are plain functions
    - Async-capable: handlers can be Celery tasks
    - Debuggable: log all events for audit
    """

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(f"Error handling event {event.event_type}")

    def publish_async(self, event: DomainEvent) -> None:
        """Publish with Celery handlers for non-critical side effects."""
        from backend.shared.tasks import dispatch_event

        dispatch_event.delay(event.event_type, event.aggregate_id, event.data)


event_bus = DomainEventBus()
