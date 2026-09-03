"""Immutable cross-domain contracts for the CyberSecGPT Native Brain.

These primitives describe capability and security-binding metadata only. They do
not implement routing, authorization, policy evaluation, model execution, tool
execution, or reasoning algorithms.
"""

from dataclasses import dataclass
from enum import StrEnum

from .exceptions import ValidationError
from .identifiers import (
    AuthorizationContextId,
    CapabilitySnapshotId,
    RequestId,
    SecurityPolicyRevisionId,
    SubstrateId,
)
from .validation import require_non_empty_string

__all__ = [
    "AvailabilityState",
    "RoutingSecurityBinding",
    "SubstrateDescriptor",
    "SubstrateKind",
    "VerificationStatus",
]


class SubstrateKind(StrEnum):
    """Identify one approved class of routable intelligence substrate."""

    NATIVE_MODEL = "native_model"
    RETRIEVAL = "retrieval"
    CLASSICAL_ML = "classical_ml"
    DOMAIN_RULE = "domain_rule"
    SYMBOLIC = "symbolic"
    GRAPH = "graph"
    TOOL = "tool"
    MEMORY = "memory"
    VERIFIER = "verifier"
    OTHER = "other"


class AvailabilityState(StrEnum):
    """Describe whether a validated substrate may currently be considered."""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    REVOKED = "revoked"
    INCOMPATIBLE = "incompatible"


class VerificationStatus(StrEnum):
    """Represent the accepted P5 verification-result status vocabulary."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    CONTRADICTORY = "contradictory"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    POLICY_BLOCKED = "policy_blocked"
    CANCELLED = "cancelled"
    DEADLINE = "deadline"
    RESOURCE_LIMIT = "resource_limit"
    VERIFICATION_ERROR = "verification_error"


def _canonical_string_tuple(
    values: tuple[str, ...],
    *,
    field_name: str,
    require_item: bool,
) -> tuple[str, ...]:
    """Validate and canonicalize an immutable tuple of unique strings."""
    if not isinstance(values, tuple):
        raise ValidationError(f"{field_name} must be a tuple")

    if require_item and not values:
        raise ValidationError(f"{field_name} must contain at least one item")

    validated = tuple(
        require_non_empty_string(value, field_name=field_name) for value in values
    )

    if len(set(validated)) != len(validated):
        raise ValidationError(f"{field_name} must not contain duplicate items")

    return tuple(sorted(validated))


@dataclass(frozen=True, slots=True)
class RoutingSecurityBinding:
    """Bind routing metadata to immutable security-relevant request state.

    This structure is deliberately not an authorization grant. It gives a later
    routing implementation stable values that must be revalidated against the
    authoritative security and policy owners before privileged execution.
    """

    request_id: RequestId
    authorization_context_id: AuthorizationContextId
    security_policy_revision_id: SecurityPolicyRevisionId
    effective_data_classification: str
    provider_network_policy: str
    offline_required: bool
    capability_snapshot_id: CapabilitySnapshotId

    def __post_init__(self) -> None:
        """Validate the immutable binding without interpreting policy semantics."""
        if not isinstance(self.request_id, RequestId):
            raise ValidationError("request_id must be a RequestId")

        if not isinstance(self.authorization_context_id, AuthorizationContextId):
            raise ValidationError(
                "authorization_context_id must be an AuthorizationContextId"
            )

        if not isinstance(
            self.security_policy_revision_id,
            SecurityPolicyRevisionId,
        ):
            raise ValidationError(
                "security_policy_revision_id must be a SecurityPolicyRevisionId"
            )

        require_non_empty_string(
            self.effective_data_classification,
            field_name="effective_data_classification",
        )
        require_non_empty_string(
            self.provider_network_policy,
            field_name="provider_network_policy",
        )

        if not isinstance(self.offline_required, bool):
            raise ValidationError("offline_required must be a bool")

        if not isinstance(self.capability_snapshot_id, CapabilitySnapshotId):
            raise ValidationError(
                "capability_snapshot_id must be a CapabilitySnapshotId"
            )


@dataclass(frozen=True, slots=True)
class SubstrateDescriptor:
    """Describe one validated routable capability without executing it.

    The descriptor contains only immutable capability metadata. It does not grant
    authorization, register itself with a router, or imply that an unavailable or
    unknown capability may be used.
    """

    substrate_id: SubstrateId
    substrate_version: str
    substrate_kind: SubstrateKind
    owner: str
    capabilities: tuple[str, ...]
    offline_capable: bool
    network_requirements: tuple[str, ...]
    data_handling_profiles: tuple[str, ...]
    availability_state: AvailabilityState
    provenance: str

    def __post_init__(self) -> None:
        """Validate and canonicalize descriptor metadata."""
        if not isinstance(self.substrate_id, SubstrateId):
            raise ValidationError("substrate_id must be a SubstrateId")

        require_non_empty_string(
            self.substrate_version,
            field_name="substrate_version",
        )

        if not isinstance(self.substrate_kind, SubstrateKind):
            raise ValidationError("substrate_kind must be a SubstrateKind")

        require_non_empty_string(self.owner, field_name="owner")

        object.__setattr__(
            self,
            "capabilities",
            _canonical_string_tuple(
                self.capabilities,
                field_name="capabilities",
                require_item=True,
            ),
        )

        if not isinstance(self.offline_capable, bool):
            raise ValidationError("offline_capable must be a bool")

        object.__setattr__(
            self,
            "network_requirements",
            _canonical_string_tuple(
                self.network_requirements,
                field_name="network_requirements",
                require_item=False,
            ),
        )
        object.__setattr__(
            self,
            "data_handling_profiles",
            _canonical_string_tuple(
                self.data_handling_profiles,
                field_name="data_handling_profiles",
                require_item=False,
            ),
        )

        if not isinstance(self.availability_state, AvailabilityState):
            raise ValidationError(
                "availability_state must be an AvailabilityState"
            )

        require_non_empty_string(self.provenance, field_name="provenance")
