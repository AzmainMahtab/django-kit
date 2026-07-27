"""Tests for Sentry initialization.

These tests verify the settings-level conditional without performing real
Sentry network I/O.
"""

import importlib
from unittest import mock

import pytest
import sentry_sdk
from django.test import Client

import backend.core.settings.base_settings as base_settings


@pytest.mark.django_db
def test_sentry_disabled_in_tests(client: Client):
    # The Sentry SDK should not be initialized when SENTRY_DSN is empty.
    assert not sentry_sdk.get_client().options.get("dsn")


def test_sentry_initializes_when_dsn_is_set(monkeypatch):
    # Re-importing base_settings with SENTRY_DSN set should call sentry_sdk.init.
    monkeypatch.setenv("SENTRY_DSN", "https://public@example.com/1")

    with mock.patch("sentry_sdk.init") as mock_init:
        importlib.reload(base_settings)

    mock_init.assert_called_once()
    call_kwargs = mock_init.call_args.kwargs
    assert call_kwargs["dsn"] == "https://public@example.com/1"
    assert call_kwargs["send_default_pii"] is False
    assert call_kwargs["environment"] == "production"
