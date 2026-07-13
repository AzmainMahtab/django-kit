"""Tests for TransitionJobStatusUseCase."""

import pytest

from backend.apps.ordering.domain.models import Job, Order
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.apps.ordering.use_cases.commands.transition_job_status import (
    TransitionJobStatusUseCase,
)
from backend.shared.exceptions import BusinessValidationError


class MockJobRepository:
    def __init__(self, job: Job):
        self.job = job

    def get_by_id(self, job_id: int) -> Job:
        return self.job

    def save(self, job: Job, update_fields=None) -> Job:
        self.job = job
        return job


def test_valid_transition():
    order = Order(id=1, order_number="ORD-001", user_id=1)
    job = Job(id=1, order=order, job_id="JOB-001", job_status=JobStateMachine.PENDING)
    use_case = TransitionJobStatusUseCase(job_repository=MockJobRepository(job))

    result = use_case.execute(
        job_id=1,
        new_status=JobStateMachine.RECEIVED_ARTWORK,
        user_id=1,
        reason="Artwork received",
    )

    assert result.job_status == JobStateMachine.RECEIVED_ARTWORK
    assert result.file_editable is False


def test_invalid_transition_raises():
    order = Order(id=1, order_number="ORD-001", user_id=1)
    job = Job(id=1, order=order, job_id="JOB-001", job_status=JobStateMachine.PENDING)
    use_case = TransitionJobStatusUseCase(job_repository=MockJobRepository(job))

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(job_id=1, new_status=JobStateMachine.BATCHED)

    assert "Cannot transition" in str(exc.value)
