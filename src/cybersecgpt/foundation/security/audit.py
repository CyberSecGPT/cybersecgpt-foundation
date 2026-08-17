"""Immutable audit-event contracts shared across CyberSecGPT boundaries."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self, cast

from ..exceptions import ValidationError
from ..identifiers import CorrelationId, Identifier, RequestId, RunId
from ..serialization import from_json as deserialize_json
from ..serialization import to_json as serialize_json
from ..typing import JsonObject
from ..utils import utc_now
from ..validation import require_non_empty_string
from .context import SecurityContext

__all__ = [
    "AuditEvent",
    "AuditEventId",
    "AuditMetadata",
    "AuditOutcome",
    "AuditSeverity",
]


_AUDIT_EVENT_KEYS = frozenset(
    {
        "event_id",
        "occurred_at",
        "severity",
        "action",
        "outcome",
        "context",
        "metadata",
    }
)

_SECURITY_CONTEXT_KEYS = frozenset(
    {
        "actor_id",
        "correlation_id",
        "request_id",
        "run_id",
    }
)


def _require_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    return require_non_empty_string(value, field_name=field_name)


def _require_object(value: object, *, field_name: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ValidationError(f"{field_name} must be a JSON object")

    return cast(JsonObject, value)


def _require_exact_keys(
    value: JsonObject,
    *,
    expected: frozenset[str],
    field_name: str,
) -> None:
    if set(value) != expected:
        raise ValidationError(f"{field_name} has an invalid field set")


@dataclass(frozen=True, slots=True)
class AuditEventId(Identifier):
    """Identify one immutable audit event."""


class AuditSeverity(StrEnum):
    """Describe the operational importance of an audit event."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditOutcome(StrEnum):
    """Describe an observed outcome reported by a higher layer."""

    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


@dataclass(frozen=True, slots=True, init=False)
class AuditMetadata:
    """Store immutable canonical JSON-object metadata."""

    _json: str = field(repr=False)

    def __init__(self, value: JsonObject | None = None) -> None:
        data: JsonObject = {} if value is None else value

        if not isinstance(data, dict):
            raise ValidationError("audit metadata must be a JSON object")

        canonical = serialize_json(data, indent=None)
        object.__setattr__(self, "_json", canonical)

    @classmethod
    def from_object(cls, value: JsonObject) -> Self:
        """Create metadata from a JSON-compatible object."""
        return cls(value)

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Create metadata from JSON text."""
        decoded = deserialize_json(payload)

        if not isinstance(decoded, dict):
            raise ValidationError("audit metadata must be a JSON object")

        return cls(cast(JsonObject, decoded))

    def to_object(self) -> JsonObject:
        """Return a fresh mutable copy."""
        return cast(JsonObject, deserialize_json(self._json))

    def to_json(self) -> str:
        """Return canonical deterministic JSON."""
        return self._json


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Represent an immutable security-relevant audit event.

    This contract records an outcome reported by a higher layer. It does not
    perform authentication, authorization, entitlement, policy, or enforcement.
    """

    event_id: AuditEventId
    occurred_at: datetime
    severity: AuditSeverity
    action: str
    outcome: AuditOutcome
    context: SecurityContext
    metadata: AuditMetadata = field(default_factory=AuditMetadata)

    def __post_init__(self) -> None:
        """Validate structural audit-event requirements."""
        if not isinstance(self.event_id, AuditEventId):
            raise ValidationError("event_id must be an AuditEventId")

        if not isinstance(self.occurred_at, datetime):
            raise ValidationError("occurred_at must be a datetime")

        offset = self.occurred_at.utcoffset()

        if offset is None:
            raise ValidationError("occurred_at must be timezone-aware")

        if offset != timedelta(0):
            raise ValidationError("occurred_at must use UTC")

        if not isinstance(self.severity, AuditSeverity):
            raise ValidationError("severity must be an AuditSeverity")

        require_non_empty_string(self.action, field_name="action")

        if not isinstance(self.outcome, AuditOutcome):
            raise ValidationError("outcome must be an AuditOutcome")

        if not isinstance(self.context, SecurityContext):
            raise ValidationError("context must be a SecurityContext")

        if not isinstance(self.metadata, AuditMetadata):
            raise ValidationError("metadata must be an AuditMetadata")

    @classmethod
    def new(
        cls,
        *,
        severity: AuditSeverity,
        action: str,
        outcome: AuditOutcome,
        context: SecurityContext,
        metadata: AuditMetadata | None = None,
    ) -> Self:
        """Create an event with a generated ID and current UTC timestamp."""
        return cls(
            event_id=AuditEventId.new(),
            occurred_at=utc_now(),
            severity=severity,
            action=action,
            outcome=outcome,
            context=context,
            metadata=metadata if metadata is not None else AuditMetadata(),
        )

    @classmethod
    def from_object(cls, value: JsonObject) -> Self:
        """Deserialize and validate an audit-event object."""
        data = _require_object(value, field_name="audit event")
        _require_exact_keys(
            data,
            expected=_AUDIT_EVENT_KEYS,
            field_name="audit event",
        )

        context_data = _require_object(
            data["context"],
            field_name="context",
        )
        _require_exact_keys(
            context_data,
            expected=_SECURITY_CONTEXT_KEYS,
            field_name="context",
        )

        occurred_at_text = _require_string(
            data["occurred_at"],
            field_name="occurred_at",
        )

        try:
            occurred_at = datetime.fromisoformat(occurred_at_text)
        except ValueError as exc:
            raise ValidationError("occurred_at must be valid ISO 8601") from exc

        severity_text = _require_string(
            data["severity"],
            field_name="severity",
        )

        try:
            severity = AuditSeverity(severity_text)
        except ValueError as exc:
            raise ValidationError("severity has an unsupported value") from exc

        outcome_text = _require_string(
            data["outcome"],
            field_name="outcome",
        )

        try:
            outcome = AuditOutcome(outcome_text)
        except ValueError as exc:
            raise ValidationError("outcome has an unsupported value") from exc

        run_value = context_data["run_id"]

        if run_value is None:
            run_id = None
        else:
            run_id = RunId(_require_string(run_value, field_name="run_id"))

        context = SecurityContext(
            actor_id=_require_string(
                context_data["actor_id"],
                field_name="actor_id",
            ),
            correlation_id=CorrelationId(
                _require_string(
                    context_data["correlation_id"],
                    field_name="correlation_id",
                )
            ),
            request_id=RequestId(
                _require_string(
                    context_data["request_id"],
                    field_name="request_id",
                )
            ),
            run_id=run_id,
        )

        metadata_data = _require_object(
            data["metadata"],
            field_name="metadata",
        )

        return cls(
            event_id=AuditEventId(
                _require_string(data["event_id"], field_name="event_id")
            ),
            occurred_at=occurred_at,
            severity=severity,
            action=_require_string(data["action"], field_name="action"),
            outcome=outcome,
            context=context,
            metadata=AuditMetadata.from_object(metadata_data),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize an audit event from JSON text."""
        decoded = deserialize_json(payload)
        data = _require_object(decoded, field_name="audit event")
        return cls.from_object(data)

    def to_object(self) -> JsonObject:
        """Return the canonical JSON-compatible representation."""
        run_id = self.context.run_id.value if self.context.run_id is not None else None

        context: JsonObject = {
            "actor_id": self.context.actor_id,
            "correlation_id": self.context.correlation_id.value,
            "request_id": self.context.request_id.value,
            "run_id": run_id,
        }

        return {
            "event_id": self.event_id.value,
            "occurred_at": self.occurred_at.isoformat(),
            "severity": self.severity.value,
            "action": self.action,
            "outcome": self.outcome.value,
            "context": context,
            "metadata": self.metadata.to_object(),
        }

    def to_json(self) -> str:
        """Serialize the audit event to deterministic JSON."""
        return serialize_json(self.to_object(), indent=None)
