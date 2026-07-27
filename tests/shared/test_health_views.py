"""Tests for shared operational endpoints."""

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_health_check_returns_200():
    client = APIClient()
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.data == {"status": "ok"}
    assert "X-Request-ID" in response.headers
