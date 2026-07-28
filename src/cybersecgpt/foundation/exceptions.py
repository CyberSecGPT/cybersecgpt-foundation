"""Exception taxonomy shared across CyberSecGPT platform components."""

__all__ = [
    "ConfigurationError",
    "FoundationError",
    "IdentifierError",
    "SerializationError",
    "ValidationError",
]


class FoundationError(Exception):
    """Base exception for errors raised by foundation primitives."""


class ConfigurationError(FoundationError):
    """Report invalid or inconsistent application configuration."""


class ValidationError(FoundationError):
    """Report data that does not satisfy a validation requirement."""


class SerializationError(FoundationError):
    """Report a failure to serialize or deserialize data."""


class IdentifierError(FoundationError):
    """Report an identifier that violates structural requirements."""
