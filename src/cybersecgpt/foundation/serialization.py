"""Deterministic and defensively bounded JSON serialization helpers."""

import json

from .constants import (
    DEFAULT_JSON_INDENT,
    MAX_JSON_CONTAINER_ITEMS,
    MAX_JSON_DEPTH,
    MAX_JSON_KEY_CHARS,
    MAX_JSON_PAYLOAD_CHARS,
    MAX_JSON_STRING_CHARS,
    MAX_JSON_TOTAL_NODES,
)
from .exceptions import SerializationError
from .validation import require_non_empty_string

__all__ = ["to_json", "from_json"]


def _decode_json(payload: str) -> object:
    """Decode JSON while translating standard-library decoder failures."""
    try:
        decoded: object = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SerializationError("payload could not be decoded as JSON") from exc
    except RecursionError as exc:
        raise SerializationError("payload exceeds supported JSON nesting") from exc

    return decoded


def _validate_json_structure(value: object) -> None:
    """Validate decoded JSON using an iterative bounded traversal."""
    stack: list[tuple[object, int]] = [(value, 0)]
    node_count = 0

    while stack:
        current, parent_depth = stack.pop()
        node_count += 1

        if node_count > MAX_JSON_TOTAL_NODES:
            raise SerializationError("JSON value exceeds maximum total node count")

        if isinstance(current, str):
            if len(current) > MAX_JSON_STRING_CHARS:
                raise SerializationError("JSON string exceeds maximum character length")
            continue

        if not isinstance(current, (list, dict)):
            continue

        container_depth = parent_depth + 1

        if container_depth > MAX_JSON_DEPTH:
            raise SerializationError("JSON value exceeds maximum nesting depth")

        if len(current) > MAX_JSON_CONTAINER_ITEMS:
            raise SerializationError("JSON container exceeds maximum item count")

        if isinstance(current, list):
            stack.extend((child, container_depth) for child in current)
            continue

        for key, child in current.items():
            if len(key) > MAX_JSON_KEY_CHARS:
                raise SerializationError(
                    "JSON object key exceeds maximum character length"
                )

            stack.append((child, container_depth))


def to_json(
    value: object,
    *,
    indent: int | None = DEFAULT_JSON_INDENT,
) -> str:
    """Serialize a value to deterministic, bounded, Unicode-preserving JSON.

    Args:
        value: JSON-compatible value to serialize.
        indent: Number of spaces used for indentation, or ``None`` for
            single-line output.

    Raises:
        SerializationError: If the value cannot be encoded or exceeds a
            Foundation JSON safety bound.
    """
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise SerializationError("value could not be serialized as JSON") from exc

    if len(encoded) > MAX_JSON_PAYLOAD_CHARS:
        raise SerializationError("encoded JSON exceeds maximum payload size")

    decoded = _decode_json(encoded)
    _validate_json_structure(decoded)

    return encoded


def from_json(payload: str) -> object:
    """Deserialize a validated and defensively bounded JSON payload.

    Args:
        payload: Non-empty JSON text without surrounding whitespace.

    Raises:
        ValidationError: If the payload is empty or has surrounding whitespace.
        SerializationError: If the payload is malformed or exceeds a Foundation
            JSON safety bound.
    """
    validated_payload = require_non_empty_string(
        payload,
        field_name="payload",
    )

    if len(validated_payload) > MAX_JSON_PAYLOAD_CHARS:
        raise SerializationError("payload exceeds maximum JSON payload size")

    decoded = _decode_json(validated_payload)
    _validate_json_structure(decoded)

    return decoded
