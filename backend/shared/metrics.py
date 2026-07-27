"""Prometheus metrics helpers and Django middleware.

Uses prometheus-client directly rather than django-prometheus so we can keep
models and the database layer untouched. Exposes a /metrics view and a
middleware that records request counts and latency per method/status/endpoint.
"""

import time

from django.http import HttpRequest, HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "django_http_requests_total",
    "Total HTTP requests",
    ["method", "status", "endpoint"],
)

REQUEST_LATENCY = Histogram(
    "django_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


def metrics_view(_request: HttpRequest) -> HttpResponse:
    """Return Prometheus exposition format metrics."""
    return HttpResponse(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST,
    )


class MetricsMiddleware:
    """Record request counts and latency for Prometheus scraping."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        method = request.method or "UNKNOWN"
        status = str(getattr(response, "status_code", 0))
        endpoint = request.resolver_match.route if request.resolver_match else request.path

        REQUEST_COUNT.labels(method=method, status=status, endpoint=endpoint).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

        return response
