"""Tests for immutable configuration contracts."""

from dataclasses import FrozenInstanceError

import pytest

from cybersecgpt.foundation import (
    Configuration,
    ConfigurationError,
    configuration,
    configuration_environment_name,
)


def test_configuration_module_exports_are_explicit() -> None:
    assert configuration.__all__ == [
        "Configuration",
        "configuration_environment_name",
    ]


def test_configuration_defaults_to_empty() -> None:
    config = Configuration()

    assert config.get("api_url") is None
    assert config.get("api_url", "fallback") == "fallback"


def test_configuration_defensively_copies_mapping() -> None:
    source = {
        "api_url": "https://example.test",
        "worker_count": "4",
    }

    config = Configuration.from_mapping(source)
    source["api_url"] = "changed"

    assert config.require("api_url") == "https://example.test"
    assert config.require("worker_count") == "4"


def test_configuration_equality_is_mapping_order_independent() -> None:
    first = Configuration(
        {
            "api_url": "one",
            "worker_count": "2",
        }
    )
    second = Configuration(
        {
            "worker_count": "2",
            "api_url": "one",
        }
    )

    assert first == second


def test_configuration_preserves_opaque_string_values() -> None:
    config = Configuration(
        {
            "empty_value": "",
            "spaced_value": " value with spaces ",
        }
    )

    assert config.require("empty_value") == ""
    assert config.require("spaced_value") == " value with spaces "


def test_configuration_repr_does_not_expose_values() -> None:
    config = Configuration({"api_token": "super-secret-value"})

    rendered = repr(config)

    assert "super-secret-value" not in rendered
    assert "api_token" not in rendered


def test_configuration_is_immutable() -> None:
    config = Configuration({"api_url": "value"})

    with pytest.raises(FrozenInstanceError):
        config._items = ()  # type: ignore[misc]


def test_configuration_rejects_non_mapping_source() -> None:
    with pytest.raises(
        ConfigurationError,
        match="mapping",
    ):
        Configuration.from_mapping(["api_url"])  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "key",
    [
        "",
        " ",
        " api_url",
        "api_url ",
        "API_URL",
        "api-url",
        "api.url",
        "_api_url",
        "1api_url",
        "api_",
        "api__url",
    ],
)
def test_configuration_rejects_invalid_keys(
    key: str,
) -> None:
    with pytest.raises(ConfigurationError):
        Configuration({key: "value"})


def test_configuration_rejects_non_string_key() -> None:
    with pytest.raises(
        ConfigurationError,
        match="key must be a string",
    ):
        Configuration({123: "value"})  # type: ignore[arg-type]


def test_configuration_accepts_lower_snake_case_keys() -> None:
    config = Configuration(
        {
            "api_url": "one",
            "api_v2_url": "two",
        }
    )

    assert config.require("api_url") == "one"
    assert config.require("api_v2_url") == "two"


def test_configuration_rejects_non_string_value() -> None:
    with pytest.raises(
        ConfigurationError,
        match="must be a string",
    ):
        Configuration({"worker_count": 4})  # type: ignore[arg-type]


def test_configuration_get_returns_existing_value() -> None:
    config = Configuration({"api_url": "configured"})

    assert config.get("api_url", "fallback") == "configured"


def test_configuration_get_rejects_invalid_default() -> None:
    config = Configuration()

    with pytest.raises(
        ConfigurationError,
        match="default",
    ):
        config.get(  # type: ignore[arg-type]
            "api_url",
            123,
        )


def test_configuration_require_rejects_missing_value() -> None:
    config = Configuration()

    with pytest.raises(
        ConfigurationError,
        match="missing",
    ):
        config.require("api_url")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("true", True),
        ("false", False),
    ],
)
def test_configuration_get_bool_parses_strict_values(
    raw: str,
    expected: bool,
) -> None:
    config = Configuration({"enabled": raw})

    assert config.get_bool("enabled") is expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "TRUE",
        "False",
        "1",
        "yes",
        "on",
        " true",
        "true ",
    ],
)
def test_configuration_get_bool_rejects_other_values(
    raw: str,
) -> None:
    config = Configuration({"enabled": raw})

    with pytest.raises(
        ConfigurationError,
        match="true or false",
    ):
        config.get_bool("enabled")


def test_configuration_get_bool_returns_default_when_missing() -> None:
    config = Configuration()

    assert config.get_bool("enabled") is None
    assert config.get_bool("enabled", True) is True


def test_configuration_get_bool_rejects_invalid_default() -> None:
    config = Configuration()

    with pytest.raises(
        ConfigurationError,
        match="default",
    ):
        config.get_bool(  # type: ignore[arg-type]
            "enabled",
            "true",
        )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", 0),
        ("42", 42),
        ("-42", -42),
        ("+7", 7),
    ],
)
def test_configuration_get_int_parses_base_ten(
    raw: str,
    expected: int,
) -> None:
    config = Configuration({"worker_count": raw})

    assert config.get_int("worker_count") == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "1_000",
        "1.0",
        "0x10",
        " 1",
        "1 ",
        "--1",
    ],
)
def test_configuration_get_int_rejects_other_values(
    raw: str,
) -> None:
    config = Configuration({"worker_count": raw})

    with pytest.raises(
        ConfigurationError,
        match="base-10 integer",
    ):
        config.get_int("worker_count")


def test_configuration_get_int_returns_default_when_missing() -> None:
    config = Configuration()

    assert config.get_int("worker_count") is None
    assert config.get_int("worker_count", 8) == 8


@pytest.mark.parametrize(
    "default",
    [
        True,
        "8",
        1.5,
    ],
)
def test_configuration_get_int_rejects_invalid_default(
    default: object,
) -> None:
    config = Configuration()

    with pytest.raises(
        ConfigurationError,
        match="default",
    ):
        config.get_int(  # type: ignore[arg-type]
            "worker_count",
            default,
        )


def test_configuration_environment_name_uses_shared_prefix() -> None:
    assert configuration_environment_name("api_url") == "CYBERSECGPT_API_URL"


@pytest.mark.parametrize(
    "key",
    [
        "",
        "API_URL",
        "api-url",
    ],
)
def test_configuration_environment_name_rejects_invalid_key(
    key: str,
) -> None:
    with pytest.raises(ConfigurationError):
        configuration_environment_name(key)
