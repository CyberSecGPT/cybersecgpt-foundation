"""Immutable application-configuration contracts."""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Self

from .constants import ENVIRONMENT_VARIABLE_PREFIX
from .exceptions import ConfigurationError

__all__ = [
    "Configuration",
    "configuration_environment_name",
]


_CONFIGURATION_KEY_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*\Z")
_INTEGER_PATTERN = re.compile(r"[+-]?[0-9]+\Z")


def _require_configuration_key(key: object) -> str:
    """Validate one canonical lower-snake-case configuration key."""
    if not isinstance(key, str):
        raise ConfigurationError("configuration key must be a string")

    if not key:
        raise ConfigurationError("configuration key must not be empty")

    if key != key.strip():
        raise ConfigurationError(
            "configuration key must not contain surrounding whitespace"
        )

    if _CONFIGURATION_KEY_PATTERN.fullmatch(key) is None:
        raise ConfigurationError("configuration key must use lower snake case")

    return key


def _require_configuration_value(
    value: object,
    *,
    key: str,
) -> str:
    """Require a configuration value to remain an opaque string."""
    if not isinstance(value, str):
        raise ConfigurationError(f"configuration value for {key!r} must be a string")

    return value


@dataclass(frozen=True, slots=True, init=False)
class Configuration:
    """Store an immutable defensive copy of application configuration.

    Keys use canonical lower snake case. Values remain opaque strings and are
    never trimmed, logged, decrypted, interpreted as secrets, or read from the
    process environment automatically.
    """

    _items: tuple[tuple[str, str], ...] = field(
        repr=False,
    )

    def __init__(
        self,
        values: Mapping[str, str] | None = None,
    ) -> None:
        """Create configuration from an optional string mapping."""
        if values is None:
            source: Mapping[str, str] = {}
        else:
            if not isinstance(values, Mapping):
                raise ConfigurationError("configuration values must be a mapping")

            source = values

        validated: list[tuple[str, str]] = []

        for raw_key, raw_value in source.items():
            key = _require_configuration_key(raw_key)
            value = _require_configuration_value(
                raw_value,
                key=key,
            )
            validated.append((key, value))

        object.__setattr__(
            self,
            "_items",
            tuple(sorted(validated)),
        )

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, str],
    ) -> Self:
        """Create configuration from a mapping using a defensive copy."""
        return cls(values)

    def _lookup(self, key: str) -> str | None:
        validated_key = _require_configuration_key(key)

        for candidate, value in self._items:
            if candidate == validated_key:
                return value

        return None

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """Return an opaque string value or a caller-supplied default."""
        if default is not None and not isinstance(default, str):
            raise ConfigurationError("configuration default must be a string or None")

        value = self._lookup(key)

        if value is None:
            return default

        return value

    def require(self, key: str) -> str:
        """Return a required value or raise ``ConfigurationError``."""
        value = self._lookup(key)

        if value is None:
            raise ConfigurationError(f"required configuration key {key!r} is missing")

        return value

    def get_bool(
        self,
        key: str,
        default: bool | None = None,
    ) -> bool | None:
        """Parse only the exact boolean strings ``true`` and ``false``."""
        if default is not None and not isinstance(default, bool):
            raise ConfigurationError(
                "boolean configuration default must be bool or None"
            )

        value = self._lookup(key)

        if value is None:
            return default

        if value == "true":
            return True

        if value == "false":
            return False

        raise ConfigurationError(
            f"configuration key {key!r} must contain true or false"
        )

    def get_int(
        self,
        key: str,
        default: int | None = None,
    ) -> int | None:
        """Parse a strict base-10 integer configuration value."""
        if default is not None and (
            isinstance(default, bool) or not isinstance(default, int)
        ):
            raise ConfigurationError(
                "integer configuration default must be int or None"
            )

        value = self._lookup(key)

        if value is None:
            return default

        if _INTEGER_PATTERN.fullmatch(value) is None:
            raise ConfigurationError(
                f"configuration key {key!r} must contain a base-10 integer"
            )

        return int(value, 10)


def configuration_environment_name(key: str) -> str:
    """Return the canonical CyberSecGPT environment-variable name."""
    validated_key = _require_configuration_key(key)

    return ENVIRONMENT_VARIABLE_PREFIX + validated_key.upper()
