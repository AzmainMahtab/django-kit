"""Shared Celery tasks used by the event bus and other infrastructure."""

from celery import shared_task
from django.utils.module_loading import import_string


@shared_task(bind=True, max_retries=3)
def dispatch_domain_event(self, event_class_path: str, payload: dict):
    """Reconstruct a domain event on a Celery worker and dispatch it.

    The event bus singleton is used so that all subscriptions registered
    during application startup are available in the worker process.
    """
    from backend.shared.event_bus import event_bus

    event_cls = import_string(event_class_path)
    event = event_cls(**payload)
    event_bus.publish(event)
