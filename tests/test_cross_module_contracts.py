"""Tests that enforce cross-module boundary rules."""

import pytest
from django.db import connection

pytestmark = pytest.mark.django_db


# These tests verify that cross-module references are ID-only (no DB FK
# constraints). If a future change re-introduces a cross-module ForeignKey,
# these assertions will fail and force an explicit architecture decision.


@pytest.fixture
def db_constraints():
    """Return a set of (table, foreign_table) for all FK constraints."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = [row[0] for row in cursor.fetchall()]

        constraints = set()
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            for row in cursor.fetchall():
                # row[2] is the referenced table
                constraints.add((table, row[2]))
        return constraints


def test_car_does_not_fk_to_owner(db_constraints):
    """Car -> Owner must be a soft ID reference, not a DB FK."""
    car_constraints = {ft for t, ft in db_constraints if t == "cars"}
    assert "owners" not in car_constraints


def test_owner_does_not_fk_to_user(db_constraints):
    """Owner -> User must be a soft ID reference, not a DB FK."""
    owner_constraints = {ft for t, ft in db_constraints if t == "owners"}
    assert "identity_user" not in owner_constraints


def test_otp_does_not_fk_to_user(db_constraints):
    """OneTimePassword -> User must be a soft ID reference, not a DB FK."""
    otp_constraints = {ft for t, ft in db_constraints if t == "otp_one_time_password"}
    assert "identity_user" not in otp_constraints


def test_rbac_user_role_does_not_fk_to_user(db_constraints):
    """UserRole -> User must be a soft ID reference, not a DB FK."""
    constraints = {ft for t, ft in db_constraints if t == "rbac_user_role"}
    assert "identity_user" not in constraints


def test_ordering_job_may_fk_to_order(db_constraints):
    """Job -> Order is an intra-module FK and is allowed."""
    job_constraints = {ft for t, ft in db_constraints if t == "ordering_job"}
    assert "ordering_order" in job_constraints
