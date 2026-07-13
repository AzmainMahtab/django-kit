"""Shared Celery tasks used by the event bus and other infrastructure."""

from celery import shared_task


@shared_task(bind=True, max_retries=3)
def dispatch_event(self, event_type: str, aggregate_id, data: dict):
    """Dispatch a domain event to all subscribed handlers asynchronously."""
    from backend.shared.domain import DomainEvent
    from backend.shared.event_bus import event_bus

    event = DomainEvent(event_type=event_type, aggregate_id=aggregate_id, data=data or {})
    event_bus.publish(event)
