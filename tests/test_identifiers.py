"""Tests for immutable typed foundation identifiers."""

from dataclasses import FrozenInstanceError, fields
from typing import cast
from uuid import UUID

import pytest

import cybersecgpt.foundation.identifiers as identifiers_module
from cybersecgpt.foundation.exceptions import IdentifierError
from cybersecgpt.foundation.identifiers import (
    AuthorizationContextId,
    CapabilitySnapshotId,
    CorrelationId,
    Identifier,
    RequestId,
    RoutingDecisionId,
    RunId,
    SecurityPolicyRevisionId,
    SubstrateId,
)


IDENTIFIER_TYPES = [
    Identifier,
    AuthorizationContextId,
    CapabilitySnapshotId,
    CorrelationId,
    RequestId,
    RoutingDecisionId,
    RunId,
    SecurityPolicyRevisionId,
    SubstrateId,
]


@pytest.mark.parametrize(
    ("identifier_type", "value"),
    [
        (Identifier, "plain"),
        (AuthorizationContextId, "authorization-context:7"),
        (CapabilitySnapshotId, "capability-snapshot/4"),
        (CorrelationId, "correlation:external-format"),
        (RequestId, "request/123"),
        (RoutingDecisionId, "routing-decision:9"),
        (RunId, "not-a-uuid"),
        (SecurityPolicyRevisionId, "security-policy:v12"),
        (SubstrateId, "substrate/native-general"),
    ],
)
def test_identifier_accepts_structurally_valid_values(
    identifier_type: type[Identifier],
    value: str,
) -> None:
    """Accept non-empty values without imposing UUID or application formats."""
    identifier = identifier_type(value)

    assert identifier.value == value
    assert str(identifier) == value


@pytest.mark.parametrize("value", ["", " ", "\t", "\n", " leading", "trailing "])
@pytest.mark.parametrize("identifier_type", IDENTIFIER_TYPES)
def test_identifier_rejects_structurally_invalid_values(
    identifier_type: type[Identifier],
    value: str,
) -> None:
    """Reject empty values and values with surrounding whitespace."""
    with pytest.raises(IdentifierError, match="Identifier value"):
        identifier_type(value)


def test_identifier_rejects_non_string_values_at_runtime() -> None:
    """Raise the public domain error at dynamically typed boundaries."""
    with pytest.raises(IdentifierError, match="must be a string"):
        Identifier(cast(str, 42))


@pytest.mark.parametrize("identifier_type", IDENTIFIER_TYPES)
def test_new_creates_uuid4_identifier_of_requested_type(
    identifier_type: type[Identifier],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a UUID4 while preserving the concrete identifier class."""
    generated_value = UUID("12345678-1234-4234-9234-123456789abc")
    monkeypatch.setattr(identifiers_module, "uuid4", lambda: generated_value)

    identifier = identifier_type.new()
    parsed_value = UUID(identifier.value)

    assert type(identifier) is identifier_type
    assert identifier.value
    assert parsed_value.version == 4


def test_generated_identifiers_are_unique(monkeypatch: pytest.MonkeyPatch) -> None:
    """Generate distinct values for separate identifiers."""
    generated_values = iter(
        (
            UUID("12345678-1234-4234-9234-123456789abc"),
            UUID("12345678-1234-4234-a234-123456789abc"),
        )
    )
    monkeypatch.setattr(identifiers_module, "uuid4", lambda: next(generated_values))

    first = RequestId.new()
    second = RequestId.new()

    assert first != second
    assert first.value != second.value


def test_identifiers_are_frozen_single_field_dataclasses() -> None:
    """Store only the immutable public value field."""
    identifier = CorrelationId("correlation-id")

    assert [field.name for field in fields(identifier)] == ["value"]
    with pytest.raises(FrozenInstanceError):
        identifier.value = "replacement"


def test_identifier_exports_are_explicit() -> None:
    """Expose exactly the documented identifier classes."""
    from cybersecgpt.foundation import identifiers

    assert identifiers.__all__ == [
        "AuthorizationContextId",
        "CapabilitySnapshotId",
        "CorrelationId",
        "Identifier",
        "RequestId",
        "RoutingDecisionId",
        "RunId",
        "SecurityPolicyRevisionId",
        "SubstrateId",
    ]
