"""Tests for deterministic JSON serialization helpers."""

import json

import pytest

from cybersecgpt.foundation.constants import (
    MAX_JSON_CONTAINER_ITEMS,
    MAX_JSON_DEPTH,
    MAX_JSON_KEY_CHARS,
    MAX_JSON_PAYLOAD_CHARS,
    MAX_JSON_STRING_CHARS,
    MAX_JSON_TOTAL_NODES,
)
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


def _nested_array(depth: int) -> object:
    value: object = 0

    for _ in range(depth):
        value = [value]

    return value


def _node_boundary_value(*, over_limit: bool = False) -> list[object]:
    container_nodes = 1 + MAX_JSON_CONTAINER_ITEMS
    scalar_nodes = MAX_JSON_TOTAL_NODES - container_nodes
    base_items, extra_items = divmod(
        scalar_nodes,
        MAX_JSON_CONTAINER_ITEMS,
    )

    groups: list[object] = [
        [0] * (base_items + (1 if index < extra_items else 0))
        for index in range(MAX_JSON_CONTAINER_ITEMS)
    ]

    if over_limit:
        last_group = groups[-1]
        assert isinstance(last_group, list)
        last_group.append(0)

    return groups


def test_from_json_accepts_exact_payload_character_limit() -> None:
    payload = "[0" + (" " * (MAX_JSON_PAYLOAD_CHARS - 3)) + "]"

    assert len(payload) == MAX_JSON_PAYLOAD_CHARS
    assert from_json(payload) == [0]


def test_from_json_rejects_payload_above_character_limit() -> None:
    payload = "[0" + (" " * (MAX_JSON_PAYLOAD_CHARS - 2)) + "]"

    assert len(payload) == MAX_JSON_PAYLOAD_CHARS + 1

    with pytest.raises(
        SerializationError,
        match="payload size",
    ):
        from_json(payload)


def test_to_json_accepts_exact_payload_character_limit() -> None:
    value = [
        "a" * MAX_JSON_STRING_CHARS,
        "b" * MAX_JSON_STRING_CHARS,
        "c" * MAX_JSON_STRING_CHARS,
        "d" * (MAX_JSON_STRING_CHARS - 16),
    ]

    payload = to_json(value, indent=None)

    assert len(payload) == MAX_JSON_PAYLOAD_CHARS


def test_to_json_rejects_output_above_character_limit() -> None:
    value = [
        "a" * MAX_JSON_STRING_CHARS,
        "b" * MAX_JSON_STRING_CHARS,
        "c" * MAX_JSON_STRING_CHARS,
        "d" * (MAX_JSON_STRING_CHARS - 15),
    ]

    with pytest.raises(
        SerializationError,
        match="payload size",
    ):
        to_json(value, indent=None)


def test_json_accepts_exact_nesting_depth_limit() -> None:
    value = _nested_array(MAX_JSON_DEPTH)
    payload = to_json(value, indent=None)

    assert from_json(payload) == value


def test_json_rejects_nesting_above_depth_limit() -> None:
    value = _nested_array(MAX_JSON_DEPTH + 1)

    with pytest.raises(
        SerializationError,
        match="nesting depth",
    ):
        to_json(value, indent=None)

    payload = "[" * (MAX_JSON_DEPTH + 1) + "0" + "]" * (MAX_JSON_DEPTH + 1)

    with pytest.raises(
        SerializationError,
        match="nesting depth",
    ):
        from_json(payload)


def test_json_accepts_exact_container_item_limit() -> None:
    value = [0] * MAX_JSON_CONTAINER_ITEMS
    payload = to_json(value, indent=None)

    assert len(from_json(payload)) == MAX_JSON_CONTAINER_ITEMS


def test_json_rejects_container_above_item_limit() -> None:
    value = [0] * (MAX_JSON_CONTAINER_ITEMS + 1)

    with pytest.raises(
        SerializationError,
        match="item count",
    ):
        to_json(value, indent=None)

    payload = json.dumps(value)

    with pytest.raises(
        SerializationError,
        match="item count",
    ):
        from_json(payload)


def test_json_accepts_exact_string_character_limit() -> None:
    value = "x" * MAX_JSON_STRING_CHARS
    payload = to_json(value, indent=None)

    assert from_json(payload) == value


def test_json_rejects_string_above_character_limit() -> None:
    value = "x" * (MAX_JSON_STRING_CHARS + 1)

    with pytest.raises(
        SerializationError,
        match="JSON string",
    ):
        to_json(value, indent=None)

    payload = json.dumps(value)

    with pytest.raises(
        SerializationError,
        match="JSON string",
    ):
        from_json(payload)


def test_json_accepts_exact_key_character_limit() -> None:
    key = "k" * MAX_JSON_KEY_CHARS
    value = {key: 1}
    payload = to_json(value, indent=None)

    assert from_json(payload) == value


def test_json_rejects_key_above_character_limit() -> None:
    key = "k" * (MAX_JSON_KEY_CHARS + 1)
    value = {key: 1}

    with pytest.raises(
        SerializationError,
        match="object key",
    ):
        to_json(value, indent=None)

    payload = json.dumps(value)

    with pytest.raises(
        SerializationError,
        match="object key",
    ):
        from_json(payload)


def test_json_accepts_exact_total_node_limit() -> None:
    value = _node_boundary_value()
    payload = to_json(value, indent=None)
    restored = from_json(payload)

    assert isinstance(restored, list)
    assert len(restored) == MAX_JSON_CONTAINER_ITEMS


def test_json_rejects_total_nodes_above_limit() -> None:
    value = _node_boundary_value(over_limit=True)

    with pytest.raises(
        SerializationError,
        match="total node count",
    ):
        to_json(value, indent=None)

    payload = json.dumps(value)

    with pytest.raises(
        SerializationError,
        match="total node count",
    ):
        from_json(payload)


def test_from_json_wraps_decoder_recursion_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_recursion(_payload: str) -> object:
        raise RecursionError("decoder recursion")

    monkeypatch.setattr(json, "loads", raise_recursion)

    with pytest.raises(SerializationError) as caught:
        from_json("0")

    assert isinstance(caught.value.__cause__, RecursionError)


def test_to_json_wraps_encoder_recursion_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_recursion(*_args: object, **_kwargs: object) -> str:
        raise RecursionError("encoder recursion")

    monkeypatch.setattr(json, "dumps", raise_recursion)

    with pytest.raises(SerializationError) as caught:
        to_json(0, indent=None)

    assert isinstance(caught.value.__cause__, RecursionError)
