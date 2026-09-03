"""Immutable security context propagated across component boundaries."""

from dataclasses import dataclass

from ..exceptions import ValidationError
from ..identifiers import CorrelationId, RequestId, RunId
from ..validation import require_non_empty_string

__all__ = ["SecurityContext"]


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
