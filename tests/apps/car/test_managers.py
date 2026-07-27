"""Tests for ORM-direct managers."""

import pytest

from backend.apps.car.domain.models import Car
from backend.apps.owner.domain.models import Owner

pytestmark = pytest.mark.django_db


def test_car_manager_get_by_license_plate():
    car = Car.objects.create(
        owner_id=1,
        make="Toyota",
        model="Camry",
        year=2020,
        color="Blue",
        license_plate="ABC123",
    )
    assert Car.objects.get_by_license_plate("ABC123") == car
    assert Car.objects.get_by_license_plate("NOTFOUND") is None


def test_car_manager_list_by_owner():
    Car.objects.create(
        owner_id=1,
        make="Toyota",
        model="Camry",
        year=2020,
        color="Blue",
        license_plate="ABC123",
    )
    Car.objects.create(
        owner_id=2,
        make="Honda",
        model="Civic",
        year=2019,
        color="Red",
        license_plate="XYZ789",
    )
    cars = list(Car.objects.list_by_owner(1))
    assert len(cars) == 1
    assert cars[0].license_plate == "ABC123"


def test_owner_manager_get_by_user_id():
    owner = Owner.objects.create(user_id=1, address="123 Main St")
    assert Owner.objects.get_by_user_id(1) == owner
    assert Owner.objects.get_by_user_id(99) is None
