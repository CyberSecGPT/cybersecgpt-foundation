"""Conservative public API for shared CyberSecGPT foundation primitives."""

from .constants import (
    DEFAULT_ENCODING,
    DEFAULT_JSON_INDENT,
    ENVIRONMENT_VARIABLE_PREFIX,
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
from .identifiers import CorrelationId, Identifier, RequestId, RunId
from .logging import configure_logging, get_logger
from .security import (
    AuditEvent,
    AuditEventId,
    AuditMetadata,
    AuditOutcome,
    AuditSeverity,
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
