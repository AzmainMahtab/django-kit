"""Additional tests for the durable event outbox."""

import pytest
from django.db import transaction

from backend.apps.event_outbox.models import DeadLetterEvent, EventOutbox
from backend.apps.event_outbox.tasks import relay_outbox_event
from backend.apps.ordering.domain.events import OrderCreated
from backend.shared.event_bus import EventBus, _outbox_publish

pytestmark = pytest.mark.django_db


def test_relay_outbox_event_publishes_and_archives():
    from backend.apps.event_outbox.models import EventStore

    bus = EventBus(durable_publisher=_outbox_publish)

    with transaction.atomic():
        bus.publish_durable(
            OrderCreated(
                aggregate_id=1,
                data={"order_id": 1, "order_number": "ORD-001", "user_id": 1, "job_ids": []},
            )
        )

    outbox = EventOutbox.objects.get()
    relay_outbox_event(str(outbox.id))

    outbox.refresh_from_db()
    assert outbox.published_at is not None
    store_entry = EventStore.objects.filter(
        event_type="ordering.order_created",
        aggregate_id="1",
    ).latest("published_at")
    assert store_entry.payload["data"]["order_number"] == "ORD-001"


def test_relay_missing_outbox_is_noop():
    relay_outbox_event("00000000-0000-0000-0000-000000000000")
    assert DeadLetterEvent.objects.count() == 0


def test_deserialization_failure_moves_to_dead_letter():
    outbox = EventOutbox.objects.create(
        event_class_path="nonexistent.module.Event",
        payload={},
    )

    relay_outbox_event(str(outbox.id))

    outbox.refresh_from_db()
    assert outbox.published_at is not None
    assert DeadLetterEvent.objects.count() == 1
