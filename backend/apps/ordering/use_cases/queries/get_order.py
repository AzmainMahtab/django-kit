"""Get order query."""

from backend.apps.ordering.domain.exceptions import OrderNotFoundError
from backend.apps.ordering.domain.models import Order
from backend.shared.domain import UseCase
from backend.shared.types import JobDTO, OrderDTO


class GetOrderUseCase(UseCase):
    """Read a single order by id."""

    def execute(self, order_id: int) -> OrderDTO:
        try:
            order = Order.objects.prefetch_related("jobs").get(pk=order_id)
        except Order.DoesNotExist as exc:
            raise OrderNotFoundError(f"Order with id {order_id} not found.") from exc

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
                for j in order.jobs.all()
            ],
        )
