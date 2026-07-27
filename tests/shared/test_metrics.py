"""Tests for the Prometheus metrics endpoint and middleware."""

import pytest
from django.test import Client
from django.urls import reverse

from backend.shared.metrics import REQUEST_COUNT, REQUEST_LATENCY


@pytest.mark.django_db
def test_metrics_endpoint_returns_prometheus_format(client: Client):
    response = client.get(reverse("metrics"))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    body = response.content.decode()
    assert "django_http_requests_total" in body
    assert "django_http_request_duration_seconds" in body


@pytest.mark.django_db
def test_metrics_middleware_records_request(client: Client):
    # Reset counters to avoid interference from previous tests.
    REQUEST_COUNT._metrics.clear()  # type: ignore[attr-defined]
    REQUEST_LATENCY._metrics.clear()  # type: ignore[attr-defined]

    response = client.get(reverse("health"))
    assert response.status_code == 200

    metric_response = client.get(reverse("metrics"))
    body = metric_response.content.decode()
    assert 'method="GET"' in body
    assert 'status="200"' in body


@pytest.mark.django_db
def test_metrics_middleware_records_404(client: Client):
    REQUEST_COUNT._metrics.clear()  # type: ignore[attr-defined]

    response = client.get("/not-a-real-page/")
    assert response.status_code == 404

    metric_response = client.get(reverse("metrics"))
    body = metric_response.content.decode()
    assert 'status="404"' in body
