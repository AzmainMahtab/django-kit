"""Tests for correlation-ID propagation into log records."""

import json
import logging

import pytest
from rest_framework.test import APIClient

from backend.shared.middleware import JsonFormatter, RequestIdFilter, get_request_id

pytestmark = pytest.mark.django_db


def _record(message="hello", exc_info=None):
    return logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=exc_info,
    )


def test_filter_attaches_a_request_id():
    record = _record()
    assert RequestIdFilter().filter(record) is True
    assert record.request_id == get_request_id()


def test_json_formatter_emits_the_request_id():
    record = _record()
    RequestIdFilter().filter(record)

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "hello"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert payload["request_id"] == record.request_id


def test_json_formatter_includes_exception_text():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _record(exc_info=sys.exc_info())

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["exception"]


def test_inbound_request_id_reaches_the_log_record(caplog):
    """The ID a client sends must be the one that lands in the logs."""
    client = APIClient()

    with caplog.at_level(logging.INFO):
        logger = logging.getLogger("test.request")
        logger.addFilter(RequestIdFilter())
        client.get("/health/", headers={"X-Request-ID": "trace-me-123"})
        logger.info("handled")

    assert caplog.records[-1].request_id == "trace-me-123"
