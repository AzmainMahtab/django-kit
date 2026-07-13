"""API integration tests for car endpoints."""

import pytest
from rest_framework.test import APIClient

from backend.apps.car.domain.models import Car
from backend.apps.identity.domain.models import User
from backend.apps.owner.domain.models import Owner

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def staff_user(client):
    user = User.objects.create_user(
        username="car_staff",
        email="car_staff@example.com",
        password="secret123",
        is_staff=True,
    )
    login = client.post(
        "/api/auth/login/",
        {"email": "car_staff@example.com", "password": "secret123"},
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access_token']}")
    return user


@pytest.fixture
def owner():
    user = User.objects.create_user(
        username="car_owner",
        email="car_owner@example.com",
        password="secret123",
    )
    return Owner.objects.create(user=user, address="123 Garage St")


def test_create_car_success(client, staff_user, owner):
    response = client.post(
        "/api/cars/",
        {
            "owner_id": owner.id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "color": "Blue",
            "license_plate": "ABC123",
        },
    )
    assert response.status_code == 201
    assert response.data["owner_id"] == owner.id
    assert response.data["license_plate"] == "ABC123"


def test_create_car_duplicate_license_plate_returns_409(client, staff_user, owner):
    Car.objects.create(
        owner=owner,
        make="Honda",
        model="Civic",
        year=2019,
        color="Red",
        license_plate="ABC123",
    )

    response = client.post(
        "/api/cars/",
        {
            "owner_id": owner.id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "color": "Blue",
            "license_plate": "ABC123",
        },
    )
    assert response.status_code == 409


def test_create_car_missing_owner_returns_404(client, staff_user):
    response = client.post(
        "/api/cars/",
        {
            "owner_id": 9999,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "color": "Blue",
            "license_plate": "ABC123",
        },
    )
    assert response.status_code == 404


def test_get_car_by_uuid(client, staff_user, owner):
    car = Car.objects.create(
        owner=owner,
        make="Honda",
        model="Civic",
        year=2019,
        color="Red",
        license_plate="XYZ789",
    )

    response = client.get(f"/api/cars/{car.uuid}/")
    assert response.status_code == 200
    assert response.data["uuid"] == str(car.uuid)


def test_list_cars_by_owner(client, staff_user, owner):
    Car.objects.create(
        owner=owner,
        make="Honda",
        model="Civic",
        year=2019,
        color="Red",
        license_plate="XYZ789",
    )

    response = client.get(f"/api/cars/by-owner/{owner.id}/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_list_cars(client, staff_user, owner):
    Car.objects.create(
        owner=owner,
        make="Honda",
        model="Civic",
        year=2019,
        color="Red",
        license_plate="XYZ789",
    )

    response = client.get("/api/cars/")
    assert response.status_code == 200
    assert response.data["count"] == 1
