"""List orders query."""

from backend.apps.ordering.domain.models import Order
from backend.shared.domain import UseCase
from backend.shared.types import JobDTO, OrderDTO


class ListOrdersUseCase(UseCase):
    """Read a list of orders with optional filters."""

    def execute(self, filters: dict | None = None) -> list[OrderDTO]:
        qs = Order.objects.prefetch_related("jobs").order_by("-created_at")
        if filters:
            qs = qs.filter(**filters)

        return [
            OrderDTO(
                id=o.id,
                order_number=o.order_number,
                user_id=o.user_id,
                status=o.status,
                jobs=[
                    JobDTO(
                        id=j.id,
                        job_id=j.job_id,
                        job_status=j.job_status,
                        file_editable=j.file_editable,
                        order_id=o.id,
                    )
                    for j in o.jobs.all()
                ],
            )
            for o in qs
        ]
