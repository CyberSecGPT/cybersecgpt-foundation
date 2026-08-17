"""Stable constant vocabulary shared across CyberSecGPT platform components."""

from typing import Final

__all__ = [
    "DEFAULT_ENCODING",
    "DEFAULT_JSON_INDENT",
    "ENVIRONMENT_VARIABLE_PREFIX",
    "MAX_JSON_CONTAINER_ITEMS",
    "MAX_JSON_DEPTH",
    "MAX_JSON_KEY_CHARS",
    "MAX_JSON_PAYLOAD_CHARS",
    "MAX_JSON_STRING_CHARS",
    "MAX_JSON_TOTAL_NODES",
    "PACKAGE_NAME",
    "PROJECT_NAME",
]

PROJECT_NAME: Final = "CyberSecGPT"
"""Human-readable name of the CyberSecGPT project."""

PACKAGE_NAME: Final = "cybersecgpt-foundation"
"""Distribution name of this foundation package."""

DEFAULT_ENCODING: Final = "utf-8"
"""Default text encoding used by foundation helpers."""

DEFAULT_JSON_INDENT: Final = 2
"""Default indentation level for JSON output."""

MAX_JSON_PAYLOAD_CHARS: Final = 1_048_576
"""Maximum accepted or emitted JSON payload length in characters."""

MAX_JSON_DEPTH: Final = 64
"""Maximum nesting depth for JSON containers."""

MAX_JSON_CONTAINER_ITEMS: Final = 10_000
"""Maximum number of entries permitted in one JSON object or array."""

MAX_JSON_TOTAL_NODES: Final = 100_000
"""Maximum number of JSON values permitted in one structure."""

MAX_JSON_STRING_CHARS: Final = 262_144
"""Maximum character length of one JSON string value."""

MAX_JSON_KEY_CHARS: Final = 4_096
"""Maximum character length of one JSON object key."""

ENVIRONMENT_VARIABLE_PREFIX: Final = "CYBERSECGPT_"
"""Prefix reserved for CyberSecGPT environment variables."""
