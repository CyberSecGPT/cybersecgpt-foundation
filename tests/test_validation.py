"""Tests for reusable foundation validation helpers."""

from typing import cast

import pytest

from cybersecgpt.foundation.exceptions import ValidationError
from cybersecgpt.foundation.validation import (
    require_non_empty_string,
    require_non_negative_integer,
    require_positive_integer,
)


@pytest.mark.parametrize("value", ["value", "internal whitespace", "0"])
def test_require_non_empty_string_returns_valid_value(value: str) -> None:
    """Return valid strings without changing their value or identity."""
    result = require_non_empty_string(value, field_name="name")

    assert result is value


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("", "label must not be empty"),
        (" \t", "label must not be empty"),
        (" leading", "label must not contain leading or trailing whitespace"),
        ("trailing\n", "label must not contain leading or trailing whitespace"),
    ],
)
def test_require_non_empty_string_rejects_invalid_text(
    value: str, message: str
) -> None:
    """Reject empty text and text with surrounding whitespace."""
    with pytest.raises(ValidationError, match=message):
        require_non_empty_string(value, field_name="label")


def test_require_non_empty_string_rejects_non_string() -> None:
    """Reject runtime values that do not satisfy the annotated contract."""
    with pytest.raises(ValidationError, match="label must be a string"):
        require_non_empty_string(cast(str, 7), field_name="label")


@pytest.mark.parametrize("value", [0, 1, 42])
def test_require_non_negative_integer_returns_valid_value(value: int) -> None:
    """Return zero and positive integer values unchanged."""
    assert require_non_negative_integer(value, field_name="count") == value


@pytest.mark.parametrize("value", [-1, -42])
def test_require_non_negative_integer_rejects_negative_value(value: int) -> None:
    """Reject negative integer values with a field-specific error."""
    with pytest.raises(ValidationError, match="count must be non-negative"):
        require_non_negative_integer(value, field_name="count")


@pytest.mark.parametrize("value", [True, False])
def test_require_non_negative_integer_rejects_boolean(value: bool) -> None:
    """Reject booleans even though they are integer subclasses."""
    with pytest.raises(ValidationError, match="count must be an integer"):
        require_non_negative_integer(value, field_name="count")


def test_require_non_negative_integer_rejects_non_integer() -> None:
    """Reject runtime values that do not satisfy the annotated contract."""
    with pytest.raises(ValidationError, match="count must be an integer"):
        require_non_negative_integer(cast(int, 1.5), field_name="count")


@pytest.mark.parametrize("value", [1, 42])
def test_require_positive_integer_returns_valid_value(value: int) -> None:
    """Return positive integer values unchanged."""
    assert require_positive_integer(value, field_name="limit") == value


@pytest.mark.parametrize("value", [0, -1, -42])
def test_require_positive_integer_rejects_non_positive_value(value: int) -> None:
    """Reject zero and negative integer values with a field-specific error."""
    with pytest.raises(ValidationError, match="limit must be positive"):
        require_positive_integer(value, field_name="limit")


@pytest.mark.parametrize("value", [True, False])
def test_require_positive_integer_rejects_boolean(value: bool) -> None:
    """Reject booleans even though they are integer subclasses."""
    with pytest.raises(ValidationError, match="limit must be an integer"):
        require_positive_integer(value, field_name="limit")


def test_require_positive_integer_rejects_non_integer() -> None:
    """Reject runtime values that do not satisfy the annotated contract."""
    with pytest.raises(ValidationError, match="limit must be an integer"):
        require_positive_integer(cast(int, 1.5), field_name="limit")


def test_validation_exports_are_explicit() -> None:
    """Publish only the supported validation helpers."""
    from cybersecgpt.foundation import validation

    assert validation.__all__ == [
        "require_non_empty_string",
        "require_non_negative_integer",
        "require_positive_integer",
    ]
