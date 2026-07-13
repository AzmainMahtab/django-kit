"""List orders query."""

from backend.apps.ordering.domain.repository_interfaces import OrderRepositoryInterface
from backend.shared.domain import UseCase
from backend.shared.types import OrderDTO


class ListOrdersUseCase(UseCase):
    """Read a list of orders with optional filters."""

    def __init__(self, order_repository: OrderRepositoryInterface = None):
        if order_repository is None:
            from backend.apps.ordering.repositories.order_repository import OrderRepository

            self.order_repo = OrderRepository()
        else:
            self.order_repo = order_repository

    def execute(self, filters: dict = None) -> list[OrderDTO]:
        orders = self.order_repo.list_orders(filters)
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
            for o in orders
        ]
