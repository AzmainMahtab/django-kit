"""Tests for the typed event bus."""

import asyncio
from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain import DomainEvent
from backend.shared.event_bus import EventBus


@dataclass
class UserCreated(DomainEvent):
    event_type: ClassVar[str] = "test.user_created"


@dataclass
class OrderPaid(DomainEvent):
    event_type: ClassVar[str] = "test.order_paid"


class TestEventBus:
    def test_subscribe_and_publish_sync(self):
        bus = EventBus()
        received = []

        def handler(event: UserCreated):
            received.append(event)

        bus.subscribe(UserCreated.event_type, handler)
        event = UserCreated(aggregate_id=1, data={"email": "a@b.com"})
        bus.publish(event)

        assert len(received) == 1
        assert received[0].aggregate_id == 1

    def test_isolated_handler_errors(self):
        bus = EventBus()
        called = []

        def bad_handler(_event):
            raise RuntimeError("boom")

        def good_handler(event):
            called.append(event)

        bus.subscribe(UserCreated.event_type, bad_handler)
        bus.subscribe(UserCreated.event_type, good_handler)

        bus.publish(UserCreated(aggregate_id=1))

        assert len(called) == 1

    def test_no_handlers_is_noop(self):
        bus = EventBus()
        bus.publish(UserCreated(aggregate_id=1))

    def test_async_handler_via_dispatch(self):
        bus = EventBus()
        received = []

        async def handler(event: UserCreated):
            received.append(event)

        bus.subscribe(UserCreated.event_type, handler)
        asyncio.run(bus.dispatch(UserCreated(aggregate_id=2)))

        assert len(received) == 1
        assert received[0].aggregate_id == 2

    def test_publish_skips_async_handlers(self, caplog):
        bus = EventBus()

        async def handler(_event):
            pass

        bus.subscribe(UserCreated.event_type, handler)
        bus.publish(UserCreated(aggregate_id=1))

        assert "Skipping async handler" in caplog.text

    def test_publish_later_serializes_event_class(self, monkeypatch):
        bus = EventBus()
        calls = []

        def fake_delay(**kwargs):
            calls.append(kwargs)

        monkeypatch.setattr(
            "backend.shared.tasks.dispatch_domain_event.delay", fake_delay
        )

        event = UserCreated(aggregate_id=42, data={"x": 1})
        bus.publish_later(event)

        assert len(calls) == 1
        assert calls[0]["event_class_path"].endswith("test_event_bus.UserCreated")
        assert calls[0]["payload"]["aggregate_id"] == 42
        assert calls[0]["payload"]["data"] == {"x": 1}
