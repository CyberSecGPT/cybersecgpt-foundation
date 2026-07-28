"""Stable constant vocabulary shared across CyberSecGPT platform components."""

from typing import Final

__all__ = [
    "DEFAULT_ENCODING",
    "DEFAULT_JSON_INDENT",
    "ENVIRONMENT_VARIABLE_PREFIX",
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

ENVIRONMENT_VARIABLE_PREFIX: Final = "CYBERSECGPT_"
"""Prefix reserved for CyberSecGPT environment variables."""
