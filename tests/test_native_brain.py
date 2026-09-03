"""Tests for immutable Native Brain cross-domain contract primitives."""

from dataclasses import FrozenInstanceError

import pytest

from cybersecgpt.foundation.exceptions import ValidationError
from cybersecgpt.foundation.identifiers import (
    AuthorizationContextId,
    CapabilitySnapshotId,
    RequestId,
    SecurityPolicyRevisionId,
    SubstrateId,
)
from cybersecgpt.foundation.native_brain import (
    AvailabilityState,
    RoutingSecurityBinding,
    SubstrateDescriptor,
    SubstrateKind,
    VerificationStatus,
)


def _binding(**overrides: object) -> RoutingSecurityBinding:
    values: dict[str, object] = {
        "request_id": RequestId("request-1"),
        "authorization_context_id": AuthorizationContextId("authorization-1"),
        "security_policy_revision_id": SecurityPolicyRevisionId("policy-7"),
        "effective_data_classification": "restricted",
        "provider_network_policy": "native-only",
        "offline_required": True,
        "capability_snapshot_id": CapabilitySnapshotId("snapshot-9"),
    }
    values.update(overrides)
    return RoutingSecurityBinding(**values)  # type: ignore[arg-type]


def _descriptor(**overrides: object) -> SubstrateDescriptor:
    values: dict[str, object] = {
        "substrate_id": SubstrateId("substrate-1"),
        "substrate_version": "1.0.0",
        "substrate_kind": SubstrateKind.NATIVE_MODEL,
        "owner": "cybersecgpt-inference",
        "capabilities": ("reason", "generate"),
        "offline_capable": True,
        "network_requirements": (),
        "data_handling_profiles": ("restricted", "internal"),
        "availability_state": AvailabilityState.AVAILABLE,
        "provenance": "sha256:artifact-1",
    }
    values.update(overrides)
    return SubstrateDescriptor(**values)  # type: ignore[arg-type]


def test_native_brain_status_vocabularies_are_stable() -> None:
    assert [item.value for item in SubstrateKind] == [
        "native_model",
        "retrieval",
        "classical_ml",
        "domain_rule",
        "symbolic",
        "graph",
        "tool",
        "memory",
        "verifier",
        "other",
    ]
    assert [item.value for item in AvailabilityState] == [
        "available",
        "degraded",
        "unavailable",
        "revoked",
        "incompatible",
    ]
    assert [item.value for item in VerificationStatus] == [
        "supported",
        "unsupported",
        "contradictory",
        "insufficient_evidence",
        "policy_blocked",
        "cancelled",
        "deadline",
        "resource_limit",
        "verification_error",
    ]


def test_routing_security_binding_preserves_opaque_security_state() -> None:
    binding = _binding()

    assert binding.request_id == RequestId("request-1")
    assert binding.authorization_context_id == AuthorizationContextId("authorization-1")
    assert binding.security_policy_revision_id == SecurityPolicyRevisionId("policy-7")
    assert binding.effective_data_classification == "restricted"
    assert binding.provider_network_policy == "native-only"
    assert binding.offline_required is True
    assert binding.capability_snapshot_id == CapabilitySnapshotId("snapshot-9")

    with pytest.raises(FrozenInstanceError):
        binding.offline_required = False  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("request_id", "request-1", "request_id"),
        ("authorization_context_id", "authorization-1", "authorization_context_id"),
        ("security_policy_revision_id", "policy-7", "security_policy_revision_id"),
        ("effective_data_classification", "", "effective_data_classification"),
        ("provider_network_policy", " network ", "provider_network_policy"),
        ("offline_required", 1, "offline_required"),
        ("capability_snapshot_id", "snapshot-9", "capability_snapshot_id"),
    ],
)
def test_routing_security_binding_rejects_invalid_fields(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        _binding(**{field_name: invalid_value})


def test_substrate_descriptor_canonicalizes_tuple_metadata() -> None:
    descriptor = _descriptor(
        capabilities=("reason", "generate"),
        network_requirements=("private-network", "loopback"),
        data_handling_profiles=("restricted", "internal"),
    )

    assert descriptor.capabilities == ("generate", "reason")
    assert descriptor.network_requirements == ("loopback", "private-network")
    assert descriptor.data_handling_profiles == ("internal", "restricted")
    assert descriptor.offline_capable is True
    assert descriptor.availability_state is AvailabilityState.AVAILABLE

    with pytest.raises(FrozenInstanceError):
        descriptor.owner = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("substrate_id", "substrate-1", "substrate_id"),
        ("substrate_version", "", "substrate_version"),
        ("substrate_kind", "native_model", "substrate_kind"),
        ("owner", " owner ", "owner"),
        ("offline_capable", 1, "offline_capable"),
        ("availability_state", "available", "availability_state"),
        ("provenance", "", "provenance"),
    ],
)
def test_substrate_descriptor_rejects_invalid_scalar_fields(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        _descriptor(**{field_name: invalid_value})


def test_substrate_descriptor_requires_immutable_capability_tuple() -> None:
    with pytest.raises(ValidationError, match="capabilities must be a tuple"):
        _descriptor(capabilities=["reason"])


def test_substrate_descriptor_requires_at_least_one_capability() -> None:
    with pytest.raises(ValidationError, match="at least one"):
        _descriptor(capabilities=())


def test_substrate_descriptor_rejects_duplicate_capabilities() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        _descriptor(capabilities=("reason", "reason"))


def test_substrate_descriptor_rejects_invalid_capability_text() -> None:
    with pytest.raises(ValidationError, match="capabilities"):
        _descriptor(capabilities=("reason", " "))


def test_substrate_descriptor_requires_network_tuple() -> None:
    with pytest.raises(ValidationError, match="network_requirements must be a tuple"):
        _descriptor(network_requirements=["loopback"])


def test_substrate_descriptor_rejects_duplicate_network_requirements() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        _descriptor(network_requirements=("loopback", "loopback"))


def test_substrate_descriptor_requires_data_handling_tuple() -> None:
    with pytest.raises(ValidationError, match="data_handling_profiles must be a tuple"):
        _descriptor(data_handling_profiles=["internal"])


def test_substrate_descriptor_rejects_duplicate_data_handling_profiles() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        _descriptor(data_handling_profiles=("internal", "internal"))


def test_native_brain_exports_are_explicit() -> None:
    from cybersecgpt.foundation import native_brain

    assert native_brain.__all__ == [
        "AvailabilityState",
        "RoutingSecurityBinding",
        "SubstrateDescriptor",
        "SubstrateKind",
        "VerificationStatus",
    ]
