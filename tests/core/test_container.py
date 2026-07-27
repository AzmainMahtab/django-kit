"""Tests for the typed dependency container."""

import pytest

from backend.core.container import AppContainer, get_container, reset_container

pytestmark = pytest.mark.django_db


def test_container_wires_all_facades():
    reset_container()
    container = get_container()

    assert container.identity is not None
    assert container.otp is not None
    assert container.rbac is not None
    assert container.owner is not None
    assert container.car is not None
    assert container.ordering is not None
    assert container.notification is not None


def test_container_is_singleton():
    reset_container()
    first = get_container()
    second = get_container()
    assert first is second


def test_container_event_bus_is_shared():
    container = AppContainer()
    assert container.car.event_bus is container.event_bus
    assert container.ordering.event_bus is container.event_bus


def test_container_registers_notification_handler():
    container = AppContainer()
    handlers = container.event_bus._handlers.get("ordering.job_status_changed", [])
    assert len(handlers) == 1


def test_reset_container_creates_new_instance():
    first = get_container()
    reset_container()
    second = get_container()
    assert first is not second
