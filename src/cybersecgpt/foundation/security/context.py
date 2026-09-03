"""Immutable security context propagated across component boundaries."""

from dataclasses import dataclass

from ..exceptions import ValidationError
from ..identifiers import (
    AuthorizationContextId,
    CapabilitySnapshotId,
    CorrelationId,
    RequestId,
    RunId,
    SecurityPolicyRevisionId,
)
from ..validation import require_non_empty_string

__all__ = ["RoutingSecurityBinding", "SecurityContext"]


@dataclass(frozen=True, slots=True)
class SecurityContext:
    """Carry opaque actor and trace identifiers across component boundaries.

    This contract contains no authentication state, credentials, roles,
    permissions, entitlements, or authorization decisions.
    """

    actor_id: str
    correlation_id: CorrelationId
    request_id: RequestId
    run_id: RunId | None = None

    def __post_init__(self) -> None:
        """Validate structural security-context requirements."""
        require_non_empty_string(self.actor_id, field_name="actor_id")

        if not isinstance(self.correlation_id, CorrelationId):
            raise ValidationError("correlation_id must be a CorrelationId")

        if not isinstance(self.request_id, RequestId):
            raise ValidationError("request_id must be a RequestId")

        if self.run_id is not None and not isinstance(self.run_id, RunId):
            raise ValidationError("run_id must be a RunId or None")


@dataclass(frozen=True, slots=True)
class RoutingSecurityBinding:
    """Bind a future routing decision to immutable security-relevant state.

    This value object is not an authorization grant and performs no policy
    evaluation. It exists so reasoning and tool layers can carry exact request,
    authorization-context, policy-revision, effective-classification,
    provider/network, offline, and capability-snapshot references without
    collapsing them into model-generated text.
    """

    request_id: RequestId
    authorization_context_id: AuthorizationContextId
    security_policy_revision_id: SecurityPolicyRevisionId
    effective_data_classification: str
    provider_network_policy: str
    offline_required: bool
    capability_snapshot_id: CapabilitySnapshotId

    def __post_init__(self) -> None:
        """Validate structure while leaving policy meaning to authoritative owners."""
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
