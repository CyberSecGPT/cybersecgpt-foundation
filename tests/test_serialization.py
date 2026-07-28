"""Tests for deterministic JSON serialization helpers."""

import json

import pytest

from cybersecgpt.foundation.exceptions import SerializationError, ValidationError
from cybersecgpt.foundation.serialization import from_json, to_json


def test_to_json_sorts_keys_and_uses_default_indentation() -> None:
    """Sort object keys and format output with the shared default indentation."""
    value = {"zeta": 2, "alpha": 1}

    assert to_json(value) == '{\n  "alpha": 1,\n  "zeta": 2\n}'


def test_to_json_preserves_unicode() -> None:
    """Keep Unicode characters readable instead of ASCII-escaping them."""
    expected = '{\n  "message": "नमस्ते 🌍"\n}'

    assert to_json({"message": "नमस्ते 🌍"}) == expected


def test_to_json_honors_custom_indentation() -> None:
    """Use a caller-provided indentation width."""
    expected = '{\n    "nested": {\n        "value": 1\n    }\n}'

    assert to_json({"nested": {"value": 1}}, indent=4) == expected


def test_to_json_supports_compact_output() -> None:
    """Produce single-line deterministic JSON when indentation is disabled."""
    expected = '{"alpha": 1, "zeta": 2}'

    assert to_json({"zeta": 2, "alpha": 1}, indent=None) == expected


def test_to_json_wraps_unserializable_value() -> None:
    """Translate unsupported values and retain the encoder exception."""
    with pytest.raises(SerializationError) as caught:
        to_json(object())

    assert isinstance(caught.value.__cause__, TypeError)


def test_to_json_wraps_circular_value() -> None:
    """Translate circular references and retain the encoder exception."""
    value: list[object] = []
    value.append(value)

    with pytest.raises(SerializationError) as caught:
        to_json(value)

    assert isinstance(caught.value.__cause__, ValueError)


def test_from_json_decodes_json_values() -> None:
    """Decode nested JSON data into its standard-library Python representation."""
    payload = '{"active":true,"items":[1,null,"value"]}'

    assert from_json(payload) == {
        "active": True,
        "items": [1, None, "value"],
    }


@pytest.mark.parametrize("payload", ["", " ", "\t", " {}", "{}\n"])
def test_from_json_rejects_invalid_payload_strings(payload: str) -> None:
    """Apply shared non-empty string validation before decoding."""
    with pytest.raises(ValidationError, match="payload"):
        from_json(payload)


def test_from_json_wraps_decoding_failure() -> None:
    """Translate malformed JSON and retain the decoder exception as the cause."""
    with pytest.raises(SerializationError) as caught:
        from_json('{"missing": }')

    assert isinstance(caught.value.__cause__, json.JSONDecodeError)


def test_serialization_exports_are_explicit() -> None:
    """Publish only the supported JSON helpers."""
    from cybersecgpt.foundation import serialization

    assert serialization.__all__ == ["to_json", "from_json"]
