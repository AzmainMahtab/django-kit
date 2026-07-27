"""Tests for durable event publishing via the outbox pattern."""

import pytest
from django.db import transaction

from backend.apps.event_outbox.models import DeadLetterEvent, EventOutbox, EventStore
from backend.apps.ordering.domain.events import JobStatusChanged, OrderCreated
from backend.shared.event_bus import EventBus, _outbox_publish, event_bus


@pytest.mark.django_db
def test_publish_durable_creates_outbox_entry():
    bus = EventBus(durable_publisher=_outbox_publish)

    with transaction.atomic():
        bus.publish_durable(
            OrderCreated(
                aggregate_id=1,
                data={"order_id": 1, "order_number": "ORD-001", "user_id": 1, "job_ids": []},
            )
        )

    outbox = EventOutbox.objects.first()
    assert outbox is not None
    assert outbox.event_class_path.endswith("OrderCreated")
    assert outbox.payload["data"]["order_number"] == "ORD-001"
    assert outbox.published_at is None


@pytest.mark.django_db
def test_publish_records_event_store():
    bus = EventBus()

    bus.publish(
        JobStatusChanged(
            aggregate_id=2,
            data={"job_id": 2, "old_status": "PENDING", "new_status": "RECEIVED_ARTWORK"},
        )
    )

    store_entry = EventStore.objects.first()
    assert store_entry is not None
    assert store_entry.event_type == "ordering.job_status_changed"


@pytest.mark.django_db
def test_publish_later_records_event_store(monkeypatch):
    bus = EventBus()
    calls = []

    def fake_delay(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr("backend.shared.tasks.dispatch_domain_event.delay", fake_delay)

    bus.publish_later(
        OrderCreated(
            aggregate_id=1,
            data={"order_id": 1, "order_number": "ORD-002", "user_id": 1, "job_ids": []},
        )
    )

    assert EventStore.objects.count() == 1
    assert len(calls) == 1


@pytest.mark.django_db
def test_global_event_bus_uses_outbox_publisher():
    assert event_bus._durable_publisher is _outbox_publish


@pytest.mark.django_db
def test_outbox_event_deserialization_failure_moves_to_dead_letter():
    outbox = EventOutbox.objects.create(
        event_class_path="nonexistent.module.Event",
        payload={},
    )

    from backend.apps.event_outbox.tasks import relay_outbox_event

    relay_outbox_event(str(outbox.id))

    outbox.refresh_from_db()
    assert outbox.published_at is not None
    assert DeadLetterEvent.objects.count() == 1
