"""Public API for the ordering module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.ordering.use_cases.commands.create_order import CreateOrderUseCase
from backend.apps.ordering.use_cases.commands.transition_job_status import (
    TransitionJobStatusUseCase,
)
from backend.apps.ordering.use_cases.queries.get_order import GetOrderUseCase
from backend.apps.ordering.use_cases.queries.list_orders import ListOrdersUseCase
from backend.shared.event_bus import EventBus


class OrderingUseCases:
    """Facade that other modules use. Internal structure is hidden."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.commands = OrderingCommands(event_bus=event_bus)
        self.queries = OrderingQueries()

    def create_order(self, **kwargs):
        return self.commands.create_order.execute(**kwargs)

    def transition_job_status(self, **kwargs):
        return self.commands.transition_job_status.execute(**kwargs)

    def get_order(self, **kwargs):
        return self.queries.get_order.execute(**kwargs)

    def list_orders(self, **kwargs):
        return self.queries.list_orders.execute(**kwargs)


class OrderingCommands:
    def __init__(self, event_bus: EventBus) -> None:
        self.create_order = CreateOrderUseCase(event_bus=event_bus)
        self.transition_job_status = TransitionJobStatusUseCase(event_bus=event_bus)


class OrderingQueries:
    def __init__(self):
        self.get_order = GetOrderUseCase()
        self.list_orders = ListOrdersUseCase()
