"""Conservative public API for shared CyberSecGPT foundation primitives."""

from .configuration import (
    Configuration,
    configuration_environment_name,
)
from .constants import (
    DEFAULT_ENCODING,
    DEFAULT_JSON_INDENT,
    ENVIRONMENT_VARIABLE_PREFIX,
    MAX_JSON_CONTAINER_ITEMS,
    MAX_JSON_DEPTH,
    MAX_JSON_KEY_CHARS,
    MAX_JSON_PAYLOAD_CHARS,
    MAX_JSON_STRING_CHARS,
    MAX_JSON_TOTAL_NODES,
    PACKAGE_NAME,
    PROJECT_NAME,
)
from .exceptions import (
    ConfigurationError,
    FoundationError,
    IdentifierError,
    SerializationError,
    ValidationError,
)
from .identifiers import (
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
from .logging import configure_logging, get_logger
from .security import (
    AuditEvent,
    AuditEventId,
    AuditMetadata,
    AuditOutcome,
    AuditSeverity,
    EvidenceRef,
    RoutingSecurityBinding,
    SecurityContext,
)
from .serialization import from_json, to_json
from .typing import JsonArray, JsonObject, JsonScalar, JsonValue
from .utils import utc_now, utc_now_iso
from .validation import (
    require_non_empty_string,
    require_non_negative_integer,
    require_positive_integer,
)
from .version import __version__

__all__ = [
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
    "Configuration",
    "configuration_environment_name",
    "FoundationError",
    "ConfigurationError",
    "ValidationError",
    "SerializationError",
    "IdentifierError",
    "Identifier",
    "AuthorizationContextId",
    "CapabilitySnapshotId",
    "CorrelationId",
    "RequestId",
    "RoutingDecisionId",
    "RunId",
    "SecurityPolicyRevisionId",
    "SubstrateId",
    "AuditEvent",
    "AuditEventId",
    "AuditMetadata",
    "AuditOutcome",
    "AuditSeverity",
    "EvidenceRef",
    "RoutingSecurityBinding",
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
]
