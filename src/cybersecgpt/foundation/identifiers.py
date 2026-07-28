"""Immutable identifiers shared across CyberSecGPT platform boundaries."""

from dataclasses import dataclass
from typing import Self
from uuid import uuid4

from .exceptions import IdentifierError

__all__ = ["CorrelationId", "Identifier", "RequestId", "RunId"]


@dataclass(frozen=True, slots=True)
class Identifier:
    """Store a non-empty identifier without imposing a value format."""

    value: str

    def __post_init__(self) -> None:
        """Validate the identifier's structural string constraints."""
        if not isinstance(self.value, str):
            raise IdentifierError("Identifier value must be a string.")
        if not self.value or self.value != self.value.strip():
            raise IdentifierError(
                "Identifier value must be non-empty and have no surrounding whitespace."
            )

    def __str__(self) -> str:
        """Return the raw identifier value."""
        return self.value

    @classmethod
    def new(cls) -> Self:
        """Create an identifier containing a new UUID4 value."""
        return cls(str(uuid4()))


@dataclass(frozen=True, slots=True)
class CorrelationId(Identifier):
    """Identify operations that belong to the same logical activity."""


@dataclass(frozen=True, slots=True)
class RequestId(Identifier):
    """Identify a single request across component boundaries."""


@dataclass(frozen=True, slots=True)
class RunId(Identifier):
    """Identify a single execution or processing run."""
