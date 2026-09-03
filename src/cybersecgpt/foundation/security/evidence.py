"""Immutable evidence-reference contracts."""

from dataclasses import dataclass
from typing import Self, cast

from ..exceptions import ValidationError
from ..serialization import from_json as deserialize_json
from ..serialization import to_json as serialize_json
from ..typing import JsonObject
from ..validation import require_non_empty_string

__all__ = ["EvidenceRef"]


_EVIDENCE_REF_KEYS = frozenset(
    {
        "source",
        "locator",
        "digest_algorithm",
        "digest",
        "media_type",
    }
)


def _require_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    return require_non_empty_string(
        value,
        field_name=field_name,
    )


def _require_object(
    value: object,
    *,
    field_name: str,
) -> JsonObject:
    if not isinstance(value, dict):
        raise ValidationError(f"{field_name} must be a JSON object")

    return cast(JsonObject, value)


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    """Reference immutable evidence without retrieving or verifying it.

    Foundation treats source, locator, digest algorithm, and digest as
    structurally validated opaque values. It does not read evidence, compute
    hashes, fetch URLs, access storage, or verify the referenced artifact.
    """

    source: str
    locator: str
    digest_algorithm: str
    digest: str
    media_type: str | None = None

    def __post_init__(self) -> None:
        """Validate structural evidence-reference requirements."""
        require_non_empty_string(
            self.source,
            field_name="source",
        )
        require_non_empty_string(
            self.locator,
            field_name="locator",
        )
        require_non_empty_string(
            self.digest_algorithm,
            field_name="digest_algorithm",
        )
        require_non_empty_string(
            self.digest,
            field_name="digest",
        )

        if self.media_type is not None:
            require_non_empty_string(
                self.media_type,
                field_name="media_type",
            )

    @classmethod
    def from_object(cls, value: JsonObject) -> Self:
        """Deserialize and validate an evidence-reference object."""
        data = _require_object(
            value,
            field_name="evidence reference",
        )

        if set(data) != _EVIDENCE_REF_KEYS:
            raise ValidationError("evidence reference has an invalid field set")

        media_type_value = data["media_type"]

        if media_type_value is None:
            media_type = None
        else:
            media_type = _require_string(
                media_type_value,
                field_name="media_type",
            )

        return cls(
            source=_require_string(
                data["source"],
                field_name="source",
            ),
            locator=_require_string(
                data["locator"],
                field_name="locator",
            ),
            digest_algorithm=_require_string(
                data["digest_algorithm"],
                field_name="digest_algorithm",
            ),
            digest=_require_string(
                data["digest"],
                field_name="digest",
            ),
            media_type=media_type,
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize an evidence reference from JSON text."""
        decoded = deserialize_json(payload)
        data = _require_object(
            decoded,
            field_name="evidence reference",
        )
        return cls.from_object(data)

    def to_object(self) -> JsonObject:
        """Return the canonical JSON-compatible representation."""
        return {
            "source": self.source,
            "locator": self.locator,
            "digest_algorithm": self.digest_algorithm,
            "digest": self.digest,
            "media_type": self.media_type,
        }

    def to_json(self) -> str:
        """Serialize the evidence reference to deterministic JSON."""
        return serialize_json(
            self.to_object(),
            indent=None,
        )
