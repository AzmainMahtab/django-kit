"""Shared middleware."""

import contextvars
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
