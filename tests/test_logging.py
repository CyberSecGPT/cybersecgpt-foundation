"""Tests for the foundation logging helpers."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import pytest

from cybersecgpt.foundation.exceptions import ValidationError
from cybersecgpt.foundation.logging import configure_logging, get_logger


@contextmanager
def isolated_root_logger() -> Iterator[logging.Logger]:
    """Provide an unconfigured root logger and restore its complete test state."""
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_filters = list(root_logger.filters)
    original_level = root_logger.level
    original_disabled = root_logger.disabled
    original_propagate = root_logger.propagate

    for handler in original_handlers:
        root_logger.removeHandler(handler)
    for log_filter in original_filters:
        root_logger.removeFilter(log_filter)
    root_logger.setLevel(logging.NOTSET)
    root_logger.disabled = False
    root_logger.propagate = True

    try:
        yield root_logger
    finally:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
            if handler not in original_handlers:
                handler.close()
        for log_filter in list(root_logger.filters):
            root_logger.removeFilter(log_filter)

        for handler in original_handlers:
            root_logger.addHandler(handler)
        for log_filter in original_filters:
            root_logger.addFilter(log_filter)
        root_logger.setLevel(original_level)
        root_logger.disabled = original_disabled
        root_logger.propagate = original_propagate


def test_configure_logging_is_idempotent() -> None:
    """Repeated configuration must retain one handler and its initial level."""
    with isolated_root_logger() as root_logger:
        configure_logging(level=logging.DEBUG)
        configured_handlers = tuple(root_logger.handlers)

        configure_logging(level=logging.ERROR)

        assert len(configured_handlers) == 1
        assert tuple(root_logger.handlers) == configured_handlers
        assert root_logger.level == logging.DEBUG


def test_configure_logging_preserves_existing_configuration() -> None:
    """An application-provided root handler and level must remain unchanged."""
    with isolated_root_logger() as root_logger:
        existing_handler = logging.NullHandler()
        root_logger.addHandler(existing_handler)
        root_logger.setLevel(logging.WARNING)

        configure_logging(level=logging.DEBUG)

        assert root_logger.handlers == [existing_handler]
        assert root_logger.level == logging.WARNING


def test_configure_logging_format_contains_required_fields() -> None:
    """The default formatter must include time, level, logger, and message."""
    with isolated_root_logger() as root_logger:
        configure_logging()
        formatter = root_logger.handlers[0].formatter
        assert formatter is not None

        record = root_logger.makeRecord(
            "cybersecgpt.test",
            logging.INFO,
            __file__,
            1,
            "security event",
            (),
            None,
        )
        rendered = formatter.format(record)

        assert formatter.formatTime(record) in rendered
        assert "INFO" in rendered
        assert "cybersecgpt.test" in rendered
        assert "security event" in rendered


def test_get_logger_returns_registered_named_logger() -> None:
    """A valid name must resolve through the standard logging registry."""
    name = "cybersecgpt.foundation.test"

    assert get_logger(name) is logging.getLogger(name)


@pytest.mark.parametrize("name", ["", " ", " leading", "trailing "])
def test_get_logger_rejects_invalid_names(name: str) -> None:
    """Invalid logger names must use the shared validation error."""
    with pytest.raises(ValidationError):
        get_logger(name)
