"""API integration tests for OTP endpoints."""

import pytest
from rest_framework.test import APIClient

from backend.apps.identity.domain.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(client):
    user = User.objects.create_user(
        username="bob",
        email="bob@example.com",
        password="secret123",
        is_active=True,
    )
    login = client.post("/api/auth/login/", {"email": "bob@example.com", "password": "secret123"})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access_token']}")
    return user


def test_generate_otp(client, user):
    response = client.post(
        "/api/otp/generate/",
        {"user_id": user.id, "otp_type": "login-otp"},
    )
    assert response.status_code == 201
    assert response.data["code"].isdigit()


def test_validate_otp(client, user):
    generated = client.post(
        "/api/otp/generate/",
        {"user_id": user.id, "otp_type": "login-otp"},
    )
    code = generated.data["code"]

    response = client.post(
        "/api/otp/validate/",
        {"user_id": user.id, "otp_type": "login-otp", "code": code},
    )
    assert response.status_code == 200
    assert response.data["success"] is True


def test_validate_otp_rejects_reuse(client, user):
    generated = client.post(
        "/api/otp/generate/",
        {"user_id": user.id, "otp_type": "login-otp"},
    )
    code = generated.data["code"]

    client.post(
        "/api/otp/validate/",
        {"user_id": user.id, "otp_type": "login-otp", "code": code},
    )
    response = client.post(
        "/api/otp/validate/",
        {"user_id": user.id, "otp_type": "login-otp", "code": code},
    )
    assert response.status_code == 401
