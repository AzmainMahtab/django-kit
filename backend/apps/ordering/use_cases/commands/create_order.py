"""Create order command."""

from backend.apps.ordering.domain.events import OrderCreated
from backend.apps.ordering.domain.models import Job, Order
from backend.apps.ordering.domain.repository_interfaces import (
    JobRepositoryInterface,
    OrderRepositoryInterface,
)
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus, event_bus as global_event_bus
from backend.shared.types import JobDTO, OrderDTO


class CreateOrderUseCase(UseCase):
    """Create a new order with one or more production jobs."""

    def __init__(
        self,
        order_repository: OrderRepositoryInterface = None,
        job_repository: JobRepositoryInterface = None,
        event_bus: EventBus = None,
    ):
        if order_repository is None:
            from backend.apps.ordering.repositories.order_repository import OrderRepository

            self.order_repo = OrderRepository()
        else:
            self.order_repo = order_repository

        if job_repository is None:
            from backend.apps.ordering.repositories.order_repository import JobRepository

            self.job_repo = JobRepository()
        else:
            self.job_repo = job_repository

        self.event_bus = event_bus or global_event_bus

    def execute(
        self,
        user_id: int,
        order_number: str,
        jobs: list[dict],
    ) -> OrderDTO:
        order = Order(order_number=order_number, user_id=user_id)
        order = self.order_repo.create(order)

        created_jobs: list[Job] = []
        for job_input in jobs:
            job = Job(
                order=order,
                job_id=job_input["job_id"],
                job_status=JobStateMachine.PENDING,
                file_editable=True,
            )
            created_jobs.append(self.job_repo.create(job))

        self.event_bus.publish(
            OrderCreated(
                aggregate_id=order.id,
                data={
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "user_id": order.user_id,
                    "job_ids": [j.job_id for j in created_jobs],
                },
            )
        )

        return self._to_dto(order, created_jobs)

    def _to_dto(self, order: Order, jobs: list[Job]) -> OrderDTO:
        return OrderDTO(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            status=order.status,
            jobs=[
                JobDTO(
                    id=j.id,
                    job_id=j.job_id,
                    job_status=j.job_status,
                    file_editable=j.file_editable,
                    order_id=order.id,
                )
                for j in jobs
            ],
        )
