"""Tests for dependency-free foundation utilities."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from cybersecgpt.foundation import utils


def test_utc_now_returns_timezone_aware_utc_datetime() -> None:
    """The current time must use the standard-library UTC singleton."""
    current = utils.utc_now()

    assert current.tzinfo is UTC
    assert current.utcoffset() == timedelta(0)


def test_utc_now_iso_uses_iso_8601_utc_text() -> None:
    """ISO output must be deterministic for a fixed timezone-aware instant."""
    fixed_time = datetime(2026, 7, 28, 14, 5, 9, 123456, tzinfo=UTC)

    with patch.object(utils, "utc_now", return_value=fixed_time):
        result = utils.utc_now_iso()

    assert result == "2026-07-28T14:05:09.123456+00:00"
    assert datetime.fromisoformat(result) == fixed_time
