"""Tests for JSON-compatible typing aliases."""

import cybersecgpt.foundation.typing as foundation_typing
from cybersecgpt.foundation.typing import (
    JsonArray,
    JsonObject,
    JsonScalar,
    JsonValue,
)


def test_json_typing_aliases_are_public_and_composable() -> None:
    """Represent nested values composed entirely of JSON-compatible types."""
    scalar: JsonScalar = "value"
    object_value: JsonObject = {"enabled": True, "name": scalar}
    array_value: JsonArray = [object_value, None, 3]
    value: JsonValue = array_value

    assert foundation_typing.__all__ == [
        "JsonScalar",
        "JsonValue",
        "JsonObject",
        "JsonArray",
    ]
    assert value == [{"enabled": True, "name": "value"}, None, 3]
