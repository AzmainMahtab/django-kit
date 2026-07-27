"""Create order command."""

from backend.apps.ordering.domain.events import OrderCreated
from backend.apps.ordering.domain.models import Job, Order
from backend.apps.ordering.domain.state_machine import JobStateMachine
from backend.shared.domain import UseCase
from backend.shared.event_bus import EventBus
from backend.shared.types import JobDTO, OrderDTO


class CreateOrderUseCase(UseCase):
    """Create a new order with one or more production jobs."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(
        self,
        user_id: int,
        order_number: str,
        jobs: list[dict],
    ) -> OrderDTO:
        order = Order.objects.create(order_number=order_number, user_id=user_id)

        created_jobs: list[Job] = []
        for job_input in jobs:
            created_jobs.append(
                Job.objects.create(
                    order=order,
                    job_id=job_input["job_id"],
                    job_status=JobStateMachine.PENDING,
                    file_editable=True,
                )
            )

        self.event_bus.publish_durable(
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
