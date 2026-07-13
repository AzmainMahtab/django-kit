"""Django ORM implementation of ordering repositories."""

from typing import Iterable

from backend.apps.ordering.domain.models import Job, Order


class OrderRepository:
    """Implements OrderRepositoryInterface using Django ORM."""

    def get_by_id(self, order_id: int) -> Order:
        return Order.objects.prefetch_related("jobs").get(pk=order_id)

    def list_orders(self, filters: dict = None) -> Iterable[Order]:
        qs = Order.objects.prefetch_related("jobs").order_by("-created_at")
        if filters:
            qs = qs.filter(**filters)
        return qs

    def create(self, order: Order) -> Order:
        order.save()
        return order

    def save(self, order: Order, update_fields: list[str] = None) -> Order:
        if update_fields:
            order.save(update_fields=update_fields)
        else:
            order.save()
        return order


class JobRepository:
    """Implements JobRepositoryInterface using Django ORM."""

    def get_by_id(self, job_id: int) -> Job:
        return Job.objects.select_related("order").get(pk=job_id)

    def get_by_job_id(self, job_id: str) -> Job:
        return Job.objects.select_related("order").get(job_id=job_id)

    def create(self, job: Job) -> Job:
        job.save()
        return job

    def save(self, job: Job, update_fields: list[str] = None) -> Job:
        if update_fields:
            job.save(update_fields=update_fields)
        else:
            job.save()
        return job
