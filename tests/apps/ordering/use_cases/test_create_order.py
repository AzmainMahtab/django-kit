"""Tests for CreateOrderUseCase."""

from backend.apps.ordering.domain.models import Job, Order
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.apps.ordering.use_cases.commands.create_order import CreateOrderUseCase


class MockOrderRepository:
    def __init__(self):
        self._orders = {}
        self._next_id = 1

    def create(self, order: Order) -> Order:
        order.id = self._next_id
        self._next_id += 1
        self._orders[order.id] = order
        return order

    def list_orders(self, filters=None):
        return list(self._orders.values())


class MockJobRepository:
    def __init__(self):
        self._jobs = {}
        self._next_id = 1

    def create(self, job: Job) -> Job:
        job.id = self._next_id
        self._next_id += 1
        self._jobs[job.id] = job
        return job


def test_create_order_publishes_event():
    from backend.shared.event_bus import EventBus

    bus = EventBus()
    order_repo = MockOrderRepository()
    job_repo = MockJobRepository()
    use_case = CreateOrderUseCase(
        order_repository=order_repo,
        job_repository=job_repo,
        event_bus=bus,
    )

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
