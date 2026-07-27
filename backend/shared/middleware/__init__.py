"""Shared middleware."""

import contextvars
import datetime
import json
import logging
import uuid

_request_id = contextvars.ContextVar("request_id", default=None)


def get_request_id():
    """Return the current request correlation ID, generating one if absent."""
    return _request_id.get() or str(uuid.uuid4())


class CorrelationIdMiddleware:
    """Propagate an ``X-Request-ID`` header across the request/response cycle."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        _request_id.set(rid)
        response = self.get_response(request)
        response["X-Request-ID"] = rid
        return response


class RequestIdFilter(logging.Filter):
    """Attach the current correlation ID to every log record.

    Installed as a filter rather than set by callers so that records emitted by
    Django, Celery and third-party libraries carry the ID without any of them
    knowing it exists.
    """

    def filter(self, record):
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    """Render records as one JSON object per line for log aggregation."""

    def format(self, record):
        payload = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)
