"""Tests for stable public foundation constants."""

from typing import Final, get_type_hints

from cybersecgpt.foundation import constants


def test_constant_values() -> None:
    """Keep shared vocabulary values stable across platform components."""
    assert constants.PROJECT_NAME == "CyberSecGPT"
    assert constants.PACKAGE_NAME == "cybersecgpt-foundation"
    assert constants.DEFAULT_ENCODING == "utf-8"
    assert constants.DEFAULT_JSON_INDENT == 2
    assert constants.ENVIRONMENT_VARIABLE_PREFIX == "CYBERSECGPT_"


def test_constants_are_annotated_as_final() -> None:
    """Declare every public constant immutable to static type checkers."""
    hints = get_type_hints(constants)

    assert hints == {
        "PROJECT_NAME": Final,
        "PACKAGE_NAME": Final,
        "DEFAULT_ENCODING": Final,
        "DEFAULT_JSON_INDENT": Final,
        "ENVIRONMENT_VARIABLE_PREFIX": Final,
    }


def test_constant_exports_are_explicit() -> None:
    """Expose exactly the stable constants through the module API."""
    assert constants.__all__ == [
        "DEFAULT_ENCODING",
        "DEFAULT_JSON_INDENT",
        "ENVIRONMENT_VARIABLE_PREFIX",
        "PACKAGE_NAME",
        "PROJECT_NAME",
    ]
