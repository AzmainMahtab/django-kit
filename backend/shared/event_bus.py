"""Typed, durable, fault-tolerant domain event bus — replaces Django signals.

Key differences from Django signals:
- Explicit subscriptions in apps.py (not scattered in signals.py).
- Event classes carry their own ``event_type``; handlers are typed by convention.
- Sync and async handlers are both supported.
- Handler errors are isolated and logged so one bad handler cannot break others.
- Durable dispatch through the outbox pattern guarantees events are not lost
  if the current process crashes.
- Events are only relayed after the current database transaction commits,
  preventing handlers from running when the business write rolls back.
- All published events are logged to ``EventStore`` for audit and replay.
"""

import asyncio
import inspect
import logging
import uuid
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Callable, TypeVar

from django.db import transaction
from django.utils.module_loading import import_string

from backend.shared.domain import DomainEvent

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=DomainEvent)
Handler = Callable[[E], Any]


class EventBus:
    """In-process event bus with durable outbox dispatch."""

    def __init__(
        self,
        durable_publisher: Callable[[DomainEvent], None] | None = None,
    ) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._durable_publisher = durable_publisher

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

        Also appends the event to the audit store. Async handlers are skipped
        in this sync path; use ``dispatch`` for mixed sync/async handlers in
        async code.
        """
        _append_event_to_store(event)
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
        await asyncio.to_thread(_append_event_to_store, event)
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await self._invoke_async(handler, event)
            else:
                await asyncio.to_thread(self._invoke, handler, event)

    # ------------------------------------------------------------------
    # Durable / out-of-process dispatch
    # ------------------------------------------------------------------
    def publish_durable(self, event: DomainEvent) -> None:
        """Publish an event durably.

        If a durable publisher was configured (typically the outbox pattern),
        the event is staged for delivery after the current DB transaction
        commits. Otherwise it falls back to in-process ``publish()``.
        """
        if self._durable_publisher:
            self._durable_publisher(event)
        else:
            self.publish(event)

    def publish_later(self, event: DomainEvent) -> None:
        """Queue the event directly on Celery for durable, out-of-process handling.

        Unlike ``publish_durable``, this does not use the outbox pattern, so
        it is not atomic with a database transaction. Use it for non-critical
        side effects where eventual delivery is acceptable.
        """
        _append_event_to_store(event)
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


def _get_correlation_id() -> str:
    """Return a correlation ID for tracing events across handlers.

    In a real system this would be pulled from request context (e.g. a
    thread-local or middleware attribute). For now we generate a fresh UUID.
    """
    return str(uuid.uuid4())


def _outbox_publish(event: DomainEvent) -> None:
    """Persist the event in the outbox and schedule relay after commit."""
    from backend.apps.event_outbox.models import EventOutbox
    from backend.apps.event_outbox.tasks import relay_outbox_event

    _append_event_to_store(event)

    outbox_entry = EventOutbox.objects.create(
        event_class_path=_class_path(event),
        payload=event.to_dict(),
    )

    outbox_id = str(outbox_entry.id)

    def _relay() -> None:
        relay_outbox_event.delay(outbox_id)

    transaction.on_commit(_relay)
    logger.debug("Staged durable event %s in outbox %s", event.event_type, outbox_id)


def _append_event_to_store(event: DomainEvent) -> None:
    """Best-effort audit log of every published event."""
    try:
        from backend.apps.event_outbox.models import EventStore

        EventStore.objects.create(
            event_type=event.event_type,
            event_class_path=_class_path(event),
            aggregate_id=str(getattr(event, "aggregate_id", "")),
            payload=event.to_dict(),
            correlation_id=_get_correlation_id(),
        )
    except Exception:
        logger.exception("Failed to append event %s to EventStore", event.event_type)


# Global singleton used by the application. Subscribers register on import or
# inside AppConfig.ready(). Tests can replace this with a fresh instance.
event_bus = EventBus(durable_publisher=_outbox_publish)
