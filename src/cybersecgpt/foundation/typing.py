"""Reusable aliases for JSON-compatible Python values."""

from typing import TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
JsonArray: TypeAlias = list[JsonValue]

__all__ = ["JsonScalar", "JsonValue", "JsonObject", "JsonArray"]
