"""Typed, in-process domain event bus — replaces Django signals.

Key differences from Django signals:
- Explicit subscriptions in apps.py (not scattered in signals.py).
- Event classes carry their own ``event_type``; handlers are typed by convention.
- Sync and async handlers are both supported.
- Handler errors are isolated and logged so one bad handler cannot break others.
- Durable dispatch through Celery reconstructs the original event class on the
  worker instead of flattening it to a string + dict.
"""

import asyncio
import inspect
import logging
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Callable, TypeVar

from django.utils.module_loading import import_string

from backend.shared.domain import DomainEvent

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=DomainEvent)
Handler = Callable[[E], Any]


class EventBus:
    """In-process event bus with optional Celery-based durable dispatch."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------
    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Register a handler for an event type.

        Handlers may be synchronous functions or coroutine functions.
        """
        self._handlers[event_type].append(handler)

    # ------------------------------------------------------------------
    # In-process dispatch
    # ------------------------------------------------------------------
    def publish(self, event: DomainEvent) -> None:
        """Invoke all synchronous handlers for *event* immediately.

        Async handlers are skipped in this sync path; use ``dispatch`` for
        mixed sync/async handlers in async code.
        """
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                logger.warning(
                    "Skipping async handler for %s in sync publish. Use dispatch() instead.",
                    event.event_type,
                )
                continue
            self._invoke(handler, event)

    async def dispatch(self, event: DomainEvent) -> None:
        """Invoke all handlers for *event* inside an async context.

        Async handlers are awaited; sync handlers are run in the thread pool
        so they do not block the event loop.
        """
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await self._invoke_async(handler, event)
            else:
                await asyncio.to_thread(self._invoke, handler, event)

    # ------------------------------------------------------------------
    # Durable / out-of-process dispatch
    # ------------------------------------------------------------------
    def publish_later(self, event: DomainEvent) -> None:
        """Queue the event on Celery for durable, out-of-process handling.

        The event class path and payload are serialized so the worker can
        reconstruct the exact event subclass and call ``publish()``.
        """
        from backend.shared.tasks import dispatch_domain_event

        dispatch_domain_event.delay(
            event_class_path=_class_path(event),
            payload=event.to_dict(),
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _invoke(self, handler: Handler, event: DomainEvent) -> None:
        try:
            handler(event)
        except Exception:
            logger.exception("Error handling event %s", event.event_type)

    async def _invoke_async(self, handler: Handler, event: DomainEvent) -> None:
        try:
            await handler(event)  # type: ignore[misc]
        except Exception:
            logger.exception("Error handling async event %s", event.event_type)


def _class_path(event: DomainEvent) -> str:
    cls = event.__class__
    return f"{cls.__module__}.{cls.__qualname__}"


# Global singleton used by the application. Subscribers register on import or
# inside AppConfig.ready(). Tests can replace this with a fresh instance.
event_bus = EventBus()
