"""API integration tests for owner endpoints."""

import pytest
from rest_framework.test import APIClient

from backend.apps.identity.domain.models import User
from backend.apps.owner.domain.models import Owner

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def staff_user(client):
    user = User.objects.create_user(
        username="owner_staff",
        email="owner_staff@example.com",
        password="secret123",
        is_staff=True,
    )
    login = client.post(
        "/api/auth/login/",
        {"email": "owner_staff@example.com", "password": "secret123"},
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access_token']}")
    return user


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="secret123",
    )


def test_create_owner_success(client, staff_user, regular_user):
    response = client.post(
        "/api/owners/",
        {"user_id": regular_user.id, "address": "123 Main St"},
    )
    assert response.status_code == 201
    assert response.data["user_id"] == regular_user.id
    assert response.data["address"] == "123 Main St"
    assert "uuid" in response.data


def test_create_owner_duplicate_user_returns_409(client, staff_user, regular_user):
    Owner.objects.create(user=regular_user, address="123 Main St")

    response = client.post(
        "/api/owners/",
        {"user_id": regular_user.id, "address": "456 Other St"},
    )
    assert response.status_code == 409


def test_get_owner_by_uuid(client, staff_user, regular_user):
    owner = Owner.objects.create(user=regular_user, address="123 Main St")

    response = client.get(f"/api/owners/{owner.uuid}/")
    assert response.status_code == 200
    assert response.data["uuid"] == str(owner.uuid)


def test_get_owner_by_user_id(client, staff_user, regular_user):
    owner = Owner.objects.create(user=regular_user, address="123 Main St")

    response = client.get(f"/api/owners/by-user/{regular_user.id}/")
    assert response.status_code == 200
    assert response.data["uuid"] == str(owner.uuid)


def test_list_owners(client, staff_user, regular_user):
    Owner.objects.create(user=regular_user, address="123 Main St")

    response = client.get("/api/owners/")
    assert response.status_code == 200
    assert response.data["count"] == 1
