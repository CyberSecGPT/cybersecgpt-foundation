"""Small validation helpers for common foundation values."""

from .exceptions import ValidationError

__all__ = [
    "require_non_empty_string",
    "require_non_negative_integer",
    "require_positive_integer",
]


def require_non_empty_string(value: str, *, field_name: str) -> str:
    """Return a non-empty string without surrounding whitespace.

    Args:
        value: String to validate.
        field_name: Name used to identify the value in validation errors.

    Raises:
        ValidationError: If the value is not a string, is empty, contains only
            whitespace, or has leading or trailing whitespace.
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    if not value or not value.strip():
        raise ValidationError(f"{field_name} must not be empty")
    if value != value.strip():
        raise ValidationError(
            f"{field_name} must not contain leading or trailing whitespace"
        )
    return value


def require_non_negative_integer(value: int, *, field_name: str) -> int:
    """Return an integer greater than or equal to zero.

    Args:
        value: Integer to validate.
        field_name: Name used to identify the value in validation errors.

    Raises:
        ValidationError: If the value is a boolean, is not an integer, or is
            negative.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer")
    if value < 0:
        raise ValidationError(f"{field_name} must be non-negative")
    return value


def require_positive_integer(value: int, *, field_name: str) -> int:
    """Return an integer greater than zero.

    Args:
        value: Integer to validate.
        field_name: Name used to identify the value in validation errors.

    Raises:
        ValidationError: If the value is a boolean, is not an integer, or is
            not positive.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer")
    if value <= 0:
        raise ValidationError(f"{field_name} must be positive")
    return value
