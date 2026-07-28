"""Deterministic JSON serialization helpers."""

import json

from .constants import DEFAULT_JSON_INDENT
from .exceptions import SerializationError
from .validation import require_non_empty_string

__all__ = ["to_json", "from_json"]


def to_json(value: object, *, indent: int | None = DEFAULT_JSON_INDENT) -> str:
    """Serialize a value to deterministic, Unicode-preserving JSON.

    Args:
        value: JSON-compatible value to serialize.
        indent: Number of spaces used for indentation, or ``None`` for compact
            output.

    Raises:
        SerializationError: If the value cannot be encoded as JSON.
    """
    try:
        return json.dumps(value, ensure_ascii=False, indent=indent, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise SerializationError("value could not be serialized as JSON") from exc


def from_json(payload: str) -> object:
    """Deserialize a validated JSON payload.

    Args:
        payload: Non-empty JSON text without surrounding whitespace.

    Raises:
        ValidationError: If the payload is empty or has surrounding whitespace.
        SerializationError: If the payload is not valid JSON.
    """
    validated_payload = require_non_empty_string(payload, field_name="payload")
    try:
        decoded: object = json.loads(validated_payload)
    except json.JSONDecodeError as exc:
        raise SerializationError("payload could not be decoded as JSON") from exc
    return decoded
