"""Get order query."""

from backend.apps.ordering.domain.exceptions import OrderNotFoundError
from backend.apps.ordering.domain.repository_interfaces import OrderRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.types import JobDTO, OrderDTO


class GetOrderUseCase(UseCase):
    """Read a single order by id."""

    def __init__(self, order_repository: OrderRepositoryInterface = None):
        if order_repository is None:
            from backend.apps.ordering.repositories.order_repository import OrderRepository

            self.order_repo = OrderRepository()
        else:
            self.order_repo = order_repository

    def execute(self, order_id: int) -> OrderDTO:
        try:
            order = self.order_repo.get_by_id(order_id)
        except Exception as exc:
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
