"""Tests for immutable security-context contracts."""

from dataclasses import FrozenInstanceError, fields

import pytest

from cybersecgpt.foundation import (
    AuthorizationContextId,
    CapabilitySnapshotId,
    CorrelationId,
    RequestId,
    RoutingSecurityBinding,
    RunId,
    SecurityContext,
    SecurityPolicyRevisionId,
    ValidationError,
)
from cybersecgpt.foundation.security import (
    RoutingSecurityBinding as RoutingSecurityBindingFromSecurity,
)
from cybersecgpt.foundation.security import (
    SecurityContext as SecurityContextFromSecurity,
)


def make_context(*, run_id: RunId | None = None) -> SecurityContext:
    """Create a valid context for tests."""
    return SecurityContext(
        actor_id="actor-123",
        correlation_id=CorrelationId("correlation-123"),
        request_id=RequestId("request-123"),
        run_id=run_id,
    )


def make_routing_binding(**overrides: object) -> RoutingSecurityBinding:
    """Create one structurally valid P5 routing security binding."""
    values: dict[str, object] = {
        "request_id": RequestId("request-123"),
        "authorization_context_id": AuthorizationContextId("authorization-123"),
        "security_policy_revision_id": SecurityPolicyRevisionId("policy-7"),
        "effective_data_classification": "restricted",
        "provider_network_policy": "native-only",
        "offline_required": True,
        "capability_snapshot_id": CapabilitySnapshotId("snapshot-5"),
    }
    values.update(overrides)
    return RoutingSecurityBinding(**values)  # type: ignore[arg-type]


def test_security_context_public_contract() -> None:
    context = make_context(run_id=RunId("run-123"))

    assert SecurityContextFromSecurity is SecurityContext
    assert tuple(field.name for field in fields(SecurityContext)) == (
        "actor_id",
        "correlation_id",
        "request_id",
        "run_id",
    )
    assert context.actor_id == "actor-123"
    assert context.run_id == RunId("run-123")


def test_security_context_run_id_optional() -> None:
    assert make_context().run_id is None


def test_security_context_is_immutable() -> None:
    context = make_context()

    with pytest.raises(FrozenInstanceError):
        context.actor_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "actor_id",
    ["", " ", " actor", "actor "],
)
def test_security_context_rejects_invalid_actor(actor_id: str) -> None:
    with pytest.raises(ValidationError):
        SecurityContext(
            actor_id=actor_id,
            correlation_id=CorrelationId("correlation"),
            request_id=RequestId("request"),
        )


def test_security_context_rejects_wrong_correlation_type() -> None:
    with pytest.raises(ValidationError, match="correlation_id"):
        SecurityContext(
            actor_id="actor",
            correlation_id=RequestId("wrong"),  # type: ignore[arg-type]
            request_id=RequestId("request"),
        )


def test_security_context_rejects_wrong_request_type() -> None:
    with pytest.raises(ValidationError, match="request_id"):
        SecurityContext(
            actor_id="actor",
            correlation_id=CorrelationId("correlation"),
            request_id=CorrelationId("wrong"),  # type: ignore[arg-type]
        )


def test_security_context_rejects_wrong_run_type() -> None:
    with pytest.raises(ValidationError, match="run_id"):
        SecurityContext(
            actor_id="actor",
            correlation_id=CorrelationId("correlation"),
            request_id=RequestId("request"),
            run_id=RequestId("wrong"),  # type: ignore[arg-type]
        )


def test_routing_security_binding_public_contract() -> None:
    binding = make_routing_binding()

    assert RoutingSecurityBindingFromSecurity is RoutingSecurityBinding
    assert tuple(field.name for field in fields(RoutingSecurityBinding)) == (
        "request_id",
        "authorization_context_id",
        "security_policy_revision_id",
        "effective_data_classification",
        "provider_network_policy",
        "offline_required",
        "capability_snapshot_id",
    )
    assert binding.request_id == RequestId("request-123")
    assert binding.authorization_context_id == AuthorizationContextId(
        "authorization-123"
    )
    assert binding.security_policy_revision_id == SecurityPolicyRevisionId("policy-7")
    assert binding.effective_data_classification == "restricted"
    assert binding.provider_network_policy == "native-only"
    assert binding.offline_required is True
    assert binding.capability_snapshot_id == CapabilitySnapshotId("snapshot-5")


def test_routing_security_binding_is_immutable() -> None:
    binding = make_routing_binding()

    with pytest.raises(FrozenInstanceError):
        binding.offline_required = False  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("request_id", "request-123", "request_id"),
        ("authorization_context_id", "authorization-123", "authorization_context_id"),
        ("security_policy_revision_id", "policy-7", "security_policy_revision_id"),
        ("effective_data_classification", "", "effective_data_classification"),
        ("effective_data_classification", " restricted", "effective_data_classification"),
        ("provider_network_policy", "", "provider_network_policy"),
        ("provider_network_policy", "native-only ", "provider_network_policy"),
        ("offline_required", 1, "offline_required"),
        ("capability_snapshot_id", "snapshot-5", "capability_snapshot_id"),
    ],
)
def test_routing_security_binding_rejects_invalid_fields(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        make_routing_binding(**{field_name: invalid_value})
