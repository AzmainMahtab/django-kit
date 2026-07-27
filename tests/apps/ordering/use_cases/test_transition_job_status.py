"""Tests for TransitionJobStatusUseCase."""

import pytest

from backend.apps.ordering.domain.events import JobStatusChanged
from backend.apps.ordering.domain.models import Job, Order
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.apps.ordering.use_cases.commands.transition_job_status import (
    TransitionJobStatusUseCase,
)
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError

pytestmark = pytest.mark.django_db


def test_valid_transition():
    order = Order.objects.create(order_number="ORD-001", user_id=1)
    job = Job.objects.create(order=order, job_id="JOB-001", job_status=JobStateMachine.PENDING)

    bus = EventBus()  # no durable publisher => publish_durable falls back to publish
    use_case = TransitionJobStatusUseCase(event_bus=bus)

    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(JobStatusChanged.event_type, handler)

    result = use_case.execute(
        job_id=job.id,
        new_status=JobStateMachine.RECEIVED_ARTWORK,
        user_id=1,
        reason="Artwork received",
    )

    assert result.job_status == JobStateMachine.RECEIVED_ARTWORK
    assert result.file_editable is False
    assert len(received) == 1
    assert received[0].event_type == "ordering.job_status_changed"


def test_invalid_transition_raises():
    order = Order.objects.create(order_number="ORD-001", user_id=1)
    job = Job.objects.create(order=order, job_id="JOB-001", job_status=JobStateMachine.PENDING)

    bus = EventBus()
    use_case = TransitionJobStatusUseCase(event_bus=bus)

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(job_id=job.id, new_status=JobStateMachine.BATCHED)

    assert "Cannot transition" in str(exc.value)
