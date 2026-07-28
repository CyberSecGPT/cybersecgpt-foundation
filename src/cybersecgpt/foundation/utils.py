"""Small dependency-free utilities shared by CyberSecGPT components."""

from datetime import UTC, datetime

__all__ = ["utc_now", "utc_now_iso"]


def utc_now() -> datetime:
    """Return the current timezone-aware UTC date and time."""
    return datetime.now(UTC)


def utc_now_iso() -> str:
    """Return the current timezone-aware UTC date and time in ISO 8601 format."""
    return utc_now().isoformat()
