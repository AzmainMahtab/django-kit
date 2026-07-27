"""Smoke tests for every registered Django admin view.

These load each changelist through the real admin site, so a misconfigured
``search_fields``, ``autocomplete_fields`` or ``list_display`` fails here rather
than in front of an operator.
"""

import pytest
from django.contrib import admin
from django.test import Client
from django.urls import reverse

from backend.apps.identity.domain.models import User
from backend.apps.otp.domain.models import OneTimePassword

pytestmark = pytest.mark.django_db

REGISTERED_MODELS = sorted(admin.site._registry, key=lambda m: m._meta.label)


@pytest.fixture
def superuser_client():
    user = User.objects.create_user(
        username="root", email="root@example.com", password="secret123", is_superuser=True
    )
    user.is_staff = True
    user.save()
    client = Client()
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.mark.parametrize("model", REGISTERED_MODELS, ids=lambda m: m._meta.label)
def test_changelist_loads(superuser_client, model):
    url = reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist")
    assert superuser_client.get(url).status_code == 200


def test_every_installed_app_with_models_is_registered():
    """A new bounded context must not silently ship without admin coverage."""
    registered = {m._meta.app_label for m in REGISTERED_MODELS}
    expected = {
        "car",
        "event_outbox",
        "identity",
        "notification",
        "ordering",
        "otp",
        "owner",
        "rbac",
    }
    assert expected <= registered


def test_otp_admin_never_exposes_the_code_hash(superuser_client):
    OneTimePassword.objects.create(
        user_id=1,
        otp_type="login",
        code_hash="argon2-hash-that-must-not-leak",
        expires_at="2099-01-01T00:00:00Z",
    )
    url = reverse("admin:otp_onetimepassword_changelist")

    body = superuser_client.get(url).content.decode()

    assert "argon2-hash-that-must-not-leak" not in body


def test_otp_admin_is_read_only(superuser_client):
    add_url = reverse("admin:otp_onetimepassword_add")
    assert superuser_client.get(add_url).status_code == 403
