"""Tests for JSON-compatible typing aliases and PEP 561 metadata."""

from importlib.resources import files

import cybersecgpt.foundation as foundation
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


def test_foundation_reexports_json_typing_aliases() -> None:
    """Publish JSON typing aliases through the conservative foundation API."""
    assert foundation.JsonScalar is foundation_typing.JsonScalar
    assert foundation.JsonValue is foundation_typing.JsonValue
    assert foundation.JsonObject is foundation_typing.JsonObject
    assert foundation.JsonArray is foundation_typing.JsonArray


def test_pep561_marker_is_packaged() -> None:
    """Expose inline type information to downstream PEP 561-aware checkers."""
    marker = files("cybersecgpt").joinpath("py.typed")

    assert marker.is_file()
