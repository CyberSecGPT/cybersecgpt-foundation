"""Tests for the public foundation exception hierarchy."""

import pytest

from cybersecgpt.foundation.exceptions import (
    ConfigurationError,
    FoundationError,
    IdentifierError,
    SerializationError,
    ValidationError,
)


@pytest.mark.parametrize(
    "exception_type",
    [
        ConfigurationError,
        ValidationError,
        SerializationError,
        IdentifierError,
    ],
)
def test_specialized_exceptions_inherit_from_foundation_error(
    exception_type: type[FoundationError],
) -> None:
    """Make every specialized error catchable through the common base class."""
    error = exception_type("failure")

    assert isinstance(error, FoundationError)
    assert isinstance(error, Exception)
    assert str(error) == "failure"


def test_exception_exports_are_explicit() -> None:
    """Expose only the documented exception types from the module API."""
    from cybersecgpt.foundation import exceptions

    assert exceptions.__all__ == [
        "ConfigurationError",
        "FoundationError",
        "IdentifierError",
        "SerializationError",
        "ValidationError",
    ]
