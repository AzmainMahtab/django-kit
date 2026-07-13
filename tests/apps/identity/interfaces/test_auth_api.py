"""API integration tests for identity authentication endpoints."""

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
        username="alice",
        email="alice@example.com",
        password="secret123",
        is_active=True,
    )
    login = client.post("/api/auth/login/", {"email": "alice@example.com", "password": "secret123"})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access_token']}")
    return user


def test_login_success(client, user):
    response = client.post(
        "/api/auth/login/",
        {"email": "alice@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.data
    assert "refresh_token" in response.data


def test_login_invalid_credentials(client, user):
    response = client.post(
        "/api/auth/login/",
        {"email": "alice@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_profile_requires_auth(client):
    response = client.get("/api/auth/profile/")
    assert response.status_code == 403


def test_profile_returns_user(client, user):
    response = client.get("/api/auth/profile/")
    assert response.status_code == 200
    assert response.data["email"] == "alice@example.com"


def test_refresh_token(client, user):
    login = client.post("/api/auth/login/", {"email": "alice@example.com", "password": "secret123"})
    refresh_token = login.data["refresh_token"]

    response = client.post("/api/auth/refresh/", {"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.data


def test_logout_revokes_token(client, user):
    login = client.post("/api/auth/login/", {"email": "alice@example.com", "password": "secret123"})
    access_token = login.data["access_token"]
    refresh_token = login.data["refresh_token"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = client.post("/api/auth/logout/", {"refresh_token": refresh_token})
    assert response.status_code == 204

    # Access token should no longer work.
    profile = client.get("/api/auth/profile/")
    assert profile.status_code in (401, 403)
