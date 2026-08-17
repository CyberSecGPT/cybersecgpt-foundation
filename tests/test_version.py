"""Tests for the public package version."""

import cybersecgpt
import cybersecgpt.foundation as foundation

EXPECTED_FOUNDATION_EXPORTS = {
    "__version__",
    "PROJECT_NAME",
    "PACKAGE_NAME",
    "DEFAULT_ENCODING",
    "DEFAULT_JSON_INDENT",
    "ENVIRONMENT_VARIABLE_PREFIX",
    "MAX_JSON_CONTAINER_ITEMS",
    "MAX_JSON_DEPTH",
    "MAX_JSON_KEY_CHARS",
    "MAX_JSON_PAYLOAD_CHARS",
    "MAX_JSON_STRING_CHARS",
    "MAX_JSON_TOTAL_NODES",
    "FoundationError",
    "ConfigurationError",
    "ValidationError",
    "SerializationError",
    "IdentifierError",
    "Identifier",
    "CorrelationId",
    "RequestId",
    "RunId",
    "AuditEvent",
    "AuditEventId",
    "AuditMetadata",
    "AuditOutcome",
    "AuditSeverity",
    "EvidenceRef",
    "SecurityContext",
    "JsonArray",
    "JsonObject",
    "JsonScalar",
    "JsonValue",
    "require_non_empty_string",
    "require_non_negative_integer",
    "require_positive_integer",
    "to_json",
    "from_json",
    "configure_logging",
    "get_logger",
    "utc_now",
    "utc_now_iso",
}


def test_public_versions_are_canonical() -> None:
    """Expose one canonical version through both package namespaces."""
    assert hasattr(cybersecgpt, "__version__")
    assert hasattr(foundation, "__version__")
    assert cybersecgpt.__version__ == "0.1.0"
    assert foundation.__version__ == "0.1.0"
    assert cybersecgpt.__version__ is foundation.__version__


def test_top_level_package_exports_only_version() -> None:
    """Keep the top-level package API limited to version metadata."""
    assert cybersecgpt.__all__ == ["__version__"]


def test_foundation_package_exports_public_primitives() -> None:
    """Expose exactly the documented conservative foundation API."""
    assert set(foundation.__all__) == EXPECTED_FOUNDATION_EXPORTS
    assert all(hasattr(foundation, name) for name in foundation.__all__)
