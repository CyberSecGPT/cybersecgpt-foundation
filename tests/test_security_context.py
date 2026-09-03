"""Tests for immutable security-context contracts."""

from dataclasses import FrozenInstanceError, fields

import pytest

from cybersecgpt.foundation import (
    CorrelationId,
    RequestId,
    RunId,
    SecurityContext,
    ValidationError,
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
