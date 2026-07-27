"""Tests for CreateOrderUseCase."""

import pytest

from backend.apps.ordering.domain.events import OrderCreated
from backend.apps.ordering.domain.models import Job, Order
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.apps.ordering.use_cases.commands.create_order import CreateOrderUseCase
from backend.shared.event_bus import EventBus

pytestmark = pytest.mark.django_db


def test_create_order_publishes_event():
    bus = EventBus()
    use_case = CreateOrderUseCase(event_bus=bus)

    received = []
    bus.subscribe("ordering.order_created", lambda e: received.append(e))

    result = use_case.execute(
        user_id=1,
        order_number="ORD-001",
        jobs=[{"job_id": "JOB-001"}, {"job_id": "JOB-002"}],
    )

    assert result.order_number == "ORD-001"
    assert result.user_id == 1
    assert len(result.jobs) == 2
    assert result.jobs[0].job_status == JobStateMachine.PENDING
    assert len(received) == 1
    assert received[0].data["order_number"] == "ORD-001"
