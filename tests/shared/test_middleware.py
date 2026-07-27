"""Tests for shared middleware."""

from django.http import HttpResponse

from backend.shared.middleware import CorrelationIdMiddleware, get_request_id


def _dummy_request(headers=None):
    class Request:
        def __init__(self):
            self.headers = headers or {}

    return Request()


def test_correlation_id_middleware_generates_id():
    def get_response(request):
        return HttpResponse()

    middleware = CorrelationIdMiddleware(get_response)
    request = _dummy_request()
    response = middleware(request)

    assert "X-Request-ID" in response
    assert response["X-Request-ID"]


def test_correlation_id_middleware_propagates_header():
    def get_response(request):
        return HttpResponse()

    middleware = CorrelationIdMiddleware(get_response)
    request = _dummy_request(headers={"X-Request-ID": "existing-id"})
    response = middleware(request)

    assert response["X-Request-ID"] == "existing-id"


def test_get_request_id_returns_current_id():
    def get_response(request):
        return HttpResponse()

    middleware = CorrelationIdMiddleware(get_response)
    request = _dummy_request(headers={"X-Request-ID": "test-id"})
    middleware(request)

    assert get_request_id() == "test-id"
