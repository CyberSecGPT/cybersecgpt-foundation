"""Tests for immutable audit-event contracts."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from cybersecgpt.foundation import (
    AuditEvent,
    AuditEventId,
    AuditMetadata,
    AuditOutcome,
    AuditSeverity,
    CorrelationId,
    Identifier,
    RequestId,
    RunId,
    SecurityContext,
    ValidationError,
)
from cybersecgpt.foundation.typing import JsonObject


def make_context(*, run_id: RunId | None = None) -> SecurityContext:
    return SecurityContext(
        actor_id="actor-123",
        correlation_id=CorrelationId("correlation-123"),
        request_id=RequestId("request-123"),
        run_id=run_id,
    )


def make_event(
    *,
    run_id: RunId | None = None,
    metadata: AuditMetadata | None = None,
) -> AuditEvent:
    return AuditEvent(
        event_id=AuditEventId("audit-123"),
        occurred_at=datetime(2026, 8, 17, 6, 30, tzinfo=UTC),
        severity=AuditSeverity.INFO,
        action="agent.tool.invoke",
        outcome=AuditOutcome.SUCCESS,
        context=make_context(run_id=run_id),
        metadata=metadata if metadata is not None else AuditMetadata(),
    )


def test_audit_event_id_is_dedicated_identifier() -> None:
    event_id = AuditEventId.new()

    assert isinstance(event_id, AuditEventId)
    assert isinstance(event_id, Identifier)
    assert event_id.value


def test_audit_enum_wire_values_are_stable() -> None:
    assert [item.value for item in AuditSeverity] == [
        "info",
        "warning",
        "error",
        "critical",
    ]
    assert [item.value for item in AuditOutcome] == [
        "success",
        "failure",
        "denied",
    ]


def test_audit_metadata_is_canonical_and_defensive() -> None:
    source: JsonObject = {
        "tool": "scanner",
        "details": {"count": 2},
    }

    metadata = AuditMetadata.from_object(source)
    source["tool"] = "changed"

    assert metadata.to_object()["tool"] == "scanner"

    copied = metadata.to_object()
    copied["tool"] = "changed-again"

    assert metadata.to_object()["tool"] == "scanner"
    assert metadata.to_json() == ('{"details": {"count": 2}, "tool": "scanner"}')


def test_audit_metadata_json_round_trip() -> None:
    metadata = AuditMetadata.from_json('{"z":1,"a":"value"}')

    assert metadata.to_json() == '{"a": "value", "z": 1}'


def test_audit_metadata_rejects_non_object() -> None:
    with pytest.raises(ValidationError, match="JSON object"):
        AuditMetadata.from_json("[]")

    with pytest.raises(ValidationError, match="JSON object"):
        AuditMetadata.from_object([])  # type: ignore[arg-type]


def test_audit_metadata_is_immutable() -> None:
    metadata = AuditMetadata({"key": "value"})

    with pytest.raises(FrozenInstanceError):
        metadata._json = "{}"  # type: ignore[misc]


def test_audit_event_new_generates_id_and_utc_time() -> None:
    event = AuditEvent.new(
        severity=AuditSeverity.WARNING,
        action="scanner.started",
        outcome=AuditOutcome.SUCCESS,
        context=make_context(),
    )

    assert isinstance(event.event_id, AuditEventId)
    assert event.occurred_at.utcoffset() == timedelta(0)
    assert event.metadata.to_object() == {}


def test_audit_event_new_preserves_metadata() -> None:
    metadata = AuditMetadata({"source": "agent"})

    event = AuditEvent.new(
        severity=AuditSeverity.ERROR,
        action="agent.failed",
        outcome=AuditOutcome.FAILURE,
        context=make_context(),
        metadata=metadata,
    )

    assert event.metadata is metadata


def test_audit_event_accepts_denied_as_recorded_outcome() -> None:
    event = AuditEvent.new(
        severity=AuditSeverity.WARNING,
        action="tool.execute",
        outcome=AuditOutcome.DENIED,
        context=make_context(),
    )

    assert event.outcome is AuditOutcome.DENIED


def test_audit_event_is_immutable() -> None:
    event = make_event()

    with pytest.raises(FrozenInstanceError):
        event.action = "changed"  # type: ignore[misc]


def test_audit_event_round_trip_with_run_id() -> None:
    event = make_event(
        run_id=RunId("run-123"),
        metadata=AuditMetadata({"tool": "scanner"}),
    )

    restored = AuditEvent.from_json(event.to_json())

    assert restored == event
    assert restored.to_object() == event.to_object()


def test_audit_event_round_trip_without_run_id() -> None:
    event = make_event()
    restored = AuditEvent.from_object(event.to_object())

    assert restored == event
    assert restored.context.run_id is None


def test_audit_event_rejects_invalid_constructor_types() -> None:
    with pytest.raises(ValidationError, match="event_id"):
        AuditEvent(
            event_id=Identifier("wrong"),  # type: ignore[arg-type]
            occurred_at=datetime.now(UTC),
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
        )

    with pytest.raises(ValidationError, match="datetime"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at="bad",  # type: ignore[arg-type]
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
        )

    with pytest.raises(ValidationError, match="severity"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime.now(UTC),
            severity="info",  # type: ignore[arg-type]
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
        )

    with pytest.raises(ValidationError, match="outcome"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime.now(UTC),
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome="success",  # type: ignore[arg-type]
            context=make_context(),
        )

    with pytest.raises(ValidationError, match="context"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime.now(UTC),
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=object(),  # type: ignore[arg-type]
        )

    with pytest.raises(ValidationError, match="metadata"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime.now(UTC),
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
            metadata={},  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("action", ["", " ", " action", "action "])
def test_audit_event_rejects_invalid_action(action: str) -> None:
    with pytest.raises(ValidationError):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime.now(UTC),
            severity=AuditSeverity.INFO,
            action=action,
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
        )


def test_audit_event_requires_timezone_aware_utc() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime(2026, 8, 17, 6, 30),
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
        )

    non_utc = timezone(timedelta(hours=5, minutes=30))

    with pytest.raises(ValidationError, match="UTC"):
        AuditEvent(
            event_id=AuditEventId("audit"),
            occurred_at=datetime(2026, 8, 17, 12, 0, tzinfo=non_utc),
            severity=AuditSeverity.INFO,
            action="audit.test",
            outcome=AuditOutcome.SUCCESS,
            context=make_context(),
        )


def test_audit_event_parser_rejects_invalid_schema() -> None:
    with pytest.raises(ValidationError, match="JSON object"):
        AuditEvent.from_json("[]")

    payload = make_event().to_object()
    payload["unexpected"] = True

    with pytest.raises(ValidationError, match="field set"):
        AuditEvent.from_object(payload)


def test_audit_event_parser_rejects_invalid_context_schema() -> None:
    payload = make_event().to_object()
    payload["context"] = {"actor_id": "actor"}

    with pytest.raises(ValidationError, match="field set"):
        AuditEvent.from_object(payload)


def test_audit_event_parser_rejects_invalid_values() -> None:
    payload = make_event().to_object()
    payload["occurred_at"] = "not-a-date"

    with pytest.raises(ValidationError, match="ISO 8601"):
        AuditEvent.from_object(payload)

    payload = make_event().to_object()
    payload["severity"] = "unknown"

    with pytest.raises(ValidationError, match="severity"):
        AuditEvent.from_object(payload)

    payload = make_event().to_object()
    payload["outcome"] = "unknown"

    with pytest.raises(ValidationError, match="outcome"):
        AuditEvent.from_object(payload)

    payload = make_event().to_object()
    context = payload["context"]
    assert isinstance(context, dict)
    context["run_id"] = 123

    with pytest.raises(ValidationError, match="run_id"):
        AuditEvent.from_object(payload)
