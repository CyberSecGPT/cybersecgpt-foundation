"""Tests for immutable evidence-reference contracts."""

from dataclasses import FrozenInstanceError

import pytest

from cybersecgpt.foundation import (
    EvidenceRef,
    ValidationError,
)
from cybersecgpt.foundation.security import (
    EvidenceRef as EvidenceRefFromSecurity,
)
from cybersecgpt.foundation.typing import JsonObject


def make_evidence(
    *,
    media_type: str | None = "application/json",
) -> EvidenceRef:
    return EvidenceRef(
        source="endpoint-agent",
        locator="artifact://host-123/sample-456",
        digest_algorithm="sha256",
        digest="abc123",
        media_type=media_type,
    )


def test_evidence_ref_public_contract() -> None:
    evidence = make_evidence()

    assert EvidenceRefFromSecurity is EvidenceRef
    assert evidence.source == "endpoint-agent"
    assert evidence.locator == ("artifact://host-123/sample-456")
    assert evidence.digest_algorithm == "sha256"
    assert evidence.digest == "abc123"
    assert evidence.media_type == "application/json"


def test_evidence_ref_media_type_is_optional() -> None:
    evidence = make_evidence(media_type=None)

    assert evidence.media_type is None


def test_evidence_ref_is_immutable() -> None:
    evidence = make_evidence()

    with pytest.raises(FrozenInstanceError):
        evidence.source = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("source", ""),
        ("source", " "),
        ("source", " agent"),
        ("source", "agent "),
        ("locator", ""),
        ("locator", " "),
        ("locator", " artifact"),
        ("locator", "artifact "),
        ("digest_algorithm", ""),
        ("digest_algorithm", " "),
        ("digest_algorithm", " sha256"),
        ("digest_algorithm", "sha256 "),
        ("digest", ""),
        ("digest", " "),
        ("digest", " abc123"),
        ("digest", "abc123 "),
    ],
)
def test_evidence_ref_rejects_invalid_required_string(
    field_name: str,
    value: str,
) -> None:
    kwargs = {
        "source": "agent",
        "locator": "artifact://sample",
        "digest_algorithm": "sha256",
        "digest": "abc123",
    }
    kwargs[field_name] = value

    with pytest.raises(ValidationError):
        EvidenceRef(**kwargs)


@pytest.mark.parametrize(
    "media_type",
    [
        "",
        " ",
        " application/json",
        "application/json ",
    ],
)
def test_evidence_ref_rejects_invalid_media_type(
    media_type: str,
) -> None:
    with pytest.raises(ValidationError):
        make_evidence(media_type=media_type)


def test_evidence_ref_accepts_extensible_digest_algorithm() -> None:
    evidence = EvidenceRef(
        source="sandbox",
        locator="artifact://sample",
        digest_algorithm="future-hash-v1",
        digest="digest-value",
    )

    assert evidence.digest_algorithm == "future-hash-v1"


def test_evidence_ref_round_trip_with_media_type() -> None:
    evidence = make_evidence()

    restored = EvidenceRef.from_json(evidence.to_json())

    assert restored == evidence
    assert restored.to_object() == evidence.to_object()


def test_evidence_ref_round_trip_without_media_type() -> None:
    evidence = make_evidence(media_type=None)

    restored = EvidenceRef.from_object(evidence.to_object())

    assert restored == evidence
    assert restored.media_type is None


def test_evidence_ref_serialization_shape() -> None:
    evidence = make_evidence()

    expected: JsonObject = {
        "source": "endpoint-agent",
        "locator": "artifact://host-123/sample-456",
        "digest_algorithm": "sha256",
        "digest": "abc123",
        "media_type": "application/json",
    }

    assert evidence.to_object() == expected


def test_evidence_ref_parser_rejects_non_object() -> None:
    with pytest.raises(
        ValidationError,
        match="JSON object",
    ):
        EvidenceRef.from_json("[]")


def test_evidence_ref_parser_rejects_invalid_field_set() -> None:
    payload = make_evidence().to_object()
    payload["unexpected"] = True

    with pytest.raises(
        ValidationError,
        match="field set",
    ):
        EvidenceRef.from_object(payload)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("source", 123),
        ("locator", 123),
        ("digest_algorithm", 123),
        ("digest", 123),
        ("media_type", 123),
    ],
)
def test_evidence_ref_parser_rejects_wrong_types(
    field_name: str,
    value: object,
) -> None:
    payload = make_evidence().to_object()
    payload[field_name] = value  # type: ignore[assignment]

    with pytest.raises(ValidationError):
        EvidenceRef.from_object(payload)
