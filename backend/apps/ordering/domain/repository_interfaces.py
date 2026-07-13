"""Ordering repository ports."""

from typing import Iterable, Protocol

from backend.apps.ordering.domain.models import Job, Order


class OrderRepositoryInterface(Protocol):
    """Port for order persistence."""

    def get_by_id(self, order_id: int) -> Order: ...

    def list_orders(self, filters: dict = None) -> Iterable[Order]: ...

    def create(self, order: Order) -> Order: ...

    def save(self, order: Order, update_fields: list[str] = None) -> Order: ...


class JobRepositoryInterface(Protocol):
    """Port for job persistence."""

    def get_by_id(self, job_id: int) -> Job: ...

    def get_by_job_id(self, job_id: str) -> Job: ...

    def create(self, job: Job) -> Job: ...

    def save(self, job: Job, update_fields: list[str] = None) -> Job: ...
