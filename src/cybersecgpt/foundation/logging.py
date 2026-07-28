"""Dependency-free logging helpers for CyberSecGPT applications."""

import logging

from .validation import require_non_empty_string

__all__ = ["configure_logging", "get_logger"]

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(*, level: int = logging.INFO) -> None:
    """Configure the root logger when the application has not configured it.

    Existing root handlers are left unchanged so applications retain control of
    their logging destinations and repeated calls do not add duplicate handlers.

    Args:
        level: Minimum severity emitted by the root logger.
    """
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    logging.basicConfig(level=level, format=_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger after validating its name.

    Args:
        name: Non-empty logger name without surrounding whitespace.

    Returns:
        The logger registered for ``name``.

    Raises:
        ValidationError: If ``name`` is empty, whitespace-only, or has
            surrounding whitespace.
    """
    return logging.getLogger(require_non_empty_string(name, field_name="name"))
