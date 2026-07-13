"""Transition job status command."""

from backend.apps.ordering.domain.events import JobStatusChanged
from backend.apps.ordering.domain.exceptions import JobNotFoundError
from backend.apps.ordering.domain.repository_interfaces import JobRepositoryInterface
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus, event_bus as global_event_bus
from backend.shared.exceptions import BusinessValidationError
from backend.shared.types import JobDTO


class TransitionJobStatusUseCase(UseCase):
    """Transition a production job through the state machine."""

    def __init__(
        self,
        job_repository: JobRepositoryInterface = None,
        event_bus: EventBus = None,
    ):
        if job_repository is None:
            from backend.apps.ordering.repositories.order_repository import JobRepository

            self.job_repo = JobRepository()
        else:
            self.job_repo = job_repository

        self.event_bus = event_bus or global_event_bus

    def execute(
        self,
        job_id: int,
        new_status: str,
        user_id: int = None,
        reason: str = None,
    ) -> JobDTO:
        try:
            job = self.job_repo.get_by_id(job_id)
        except Exception as exc:
            raise JobNotFoundError(f"Job with id {job_id} not found.") from exc

        old_status = job.job_status

        if new_status not in JobStateMachine.TRANSITIONS:
            raise BusinessValidationError(f"Unknown job status: {new_status}")

        JobStateMachine.assert_transition(old_status, new_status)

        job.job_status = new_status
        job.file_editable = JobStateMachine.is_file_editable(new_status)
        self.job_repo.save(job, update_fields=["job_status", "file_editable", "updated_at"])

        self.event_bus.publish(
            JobStatusChanged(
                aggregate_id=job.id,
                data={
                    "job_id": job.id,
                    "job_uuid": job.job_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "user_id": user_id,
                    "reason": reason or f"Status: {old_status} -> {new_status}",
                },
            )
        )

        return JobDTO(
            id=job.id,
            job_id=job.job_id,
            job_status=job.job_status,
            file_editable=job.file_editable,
            order_id=job.order_id,
        )
