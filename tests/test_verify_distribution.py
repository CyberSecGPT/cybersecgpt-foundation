"""Tests for distribution boundary verification helpers."""

from email.message import Message

import pytest
from scripts import verify_distribution as verify


def _metadata_with_version(version: str) -> Message:
    """Build metadata containing a single Metadata-Version header."""
    metadata = Message()
    metadata["Metadata-Version"] = version
    return metadata


@pytest.mark.parametrize("value", ["2.4", "2.5"])
def test_parse_metadata_version_accepts_supported_values(value: str) -> None:
    """Parse known Core Metadata versions into major and minor components."""
    major, minor = value.split(".")
    assert verify._parse_metadata_version(value) == (int(major), int(minor))


@pytest.mark.parametrize("value", ["", "2", "2.4.1", "a.b", "2.a"])
def test_parse_metadata_version_rejects_malformed_values(value: str) -> None:
    """Reject metadata versions that are not major.minor integers."""
    with pytest.raises(verify.DistributionVerificationError, match="malformed"):
        verify._parse_metadata_version(value)


@pytest.mark.parametrize("version", ["2.4", "2.5"])
def test_verify_metadata_version_accepts_known_versions(version: str) -> None:
    """Accept Core Metadata versions required by current packaging output."""
    verify._verify_metadata_version(_metadata_with_version(version), "test metadata")


def test_verify_metadata_version_rejects_below_minimum() -> None:
    """Reject metadata older than the PEP 639 license fields require."""
    with pytest.raises(verify.DistributionVerificationError, match="at least 2.4"):
        verify._verify_metadata_version(_metadata_with_version("2.3"), "test metadata")


def test_verify_metadata_version_warns_for_future_minor_version() -> None:
    """Accept future 2.x minors above the highest known version with a warning."""
    with pytest.warns(UserWarning, match="newer than the highest known version"):
        verify._verify_metadata_version(_metadata_with_version("2.6"), "test metadata")


def test_verify_metadata_version_rejects_unsupported_major() -> None:
    """Reject metadata whose major version exceeds supported major version 2."""
    with pytest.raises(
        verify.DistributionVerificationError, match="unsupported Metadata-Version major"
    ):
        verify._verify_metadata_version(_metadata_with_version("3.0"), "test metadata")


def test_verify_metadata_version_rejects_missing_header() -> None:
    """Require exactly one Metadata-Version header."""
    with pytest.raises(verify.DistributionVerificationError, match="must occur once"):
        verify._verify_metadata_version(Message(), "test metadata")


def test_verify_metadata_version_rejects_duplicate_header() -> None:
    """Reject duplicate Metadata-Version headers."""
    metadata = Message()
    metadata["Metadata-Version"] = "2.4"
    metadata["Metadata-Version"] = "2.5"

    with pytest.raises(verify.DistributionVerificationError, match="must occur once"):
        verify._verify_metadata_version(metadata, "test metadata")


@pytest.mark.parametrize(
    ("requirement", "expected"),
    [
        ("pytest>=8.3,<9; extra == 'dev'", "pytest"),
        ('black>=24.10,<26; extra == "dev"', "black"),
        ("mypy>=1.13,<2; extra == 'dev'", "mypy"),
        ("pytest-cov>=6,<7; extra == 'dev'", "pytest-cov"),
    ],
)
def test_parse_dev_requires_dist_extracts_pinned_packages(
    requirement: str, expected: str
) -> None:
    """Extract dev package names from pinned Requires-Dist entries."""
    assert verify._parse_dev_requires_dist(requirement) == expected


def test_verify_dev_requirements_accepts_pinned_dev_extra() -> None:
    """Accept the bounded dev dependency set declared in project metadata."""
    requirements = [
        "black>=24.10,<26; extra == 'dev'",
        "build>=1.2,<2; extra == 'dev'",
        "mypy>=1.13,<2; extra == 'dev'",
        "pytest>=8.3,<9; extra == 'dev'",
        "pytest-cov>=6,<7; extra == 'dev'",
        "ruff>=0.9,<1; extra == 'dev'",
    ]

    verify._verify_dev_requirements(requirements, "test metadata")


def test_verify_dev_requirements_rejects_missing_package() -> None:
    """Reject dev metadata that omits a required package."""
    requirements = [
        "black>=24.10,<26; extra == 'dev'",
        "build>=1.2,<2; extra == 'dev'",
        "mypy>=1.13,<2; extra == 'dev'",
        "pytest>=8.3,<9; extra == 'dev'",
        "pytest-cov>=6,<7; extra == 'dev'",
    ]

    with pytest.raises(
        verify.DistributionVerificationError, match="dependency set is incorrect"
    ):
        verify._verify_dev_requirements(requirements, "test metadata")


def test_verify_dev_requirements_rejects_unexpected_package() -> None:
    """Reject dev metadata that includes an unexpected package."""
    requirements = [
        "black>=24.10,<26; extra == 'dev'",
        "build>=1.2,<2; extra == 'dev'",
        "mypy>=1.13,<2; extra == 'dev'",
        "pytest>=8.3,<9; extra == 'dev'",
        "pytest-cov>=6,<7; extra == 'dev'",
        "ruff>=0.9,<1; extra == 'dev'",
        "requests>=2,<3; extra == 'dev'",
    ]

    with pytest.raises(
        verify.DistributionVerificationError, match="dependency set is incorrect"
    ):
        verify._verify_dev_requirements(requirements, "test metadata")


def test_verify_dev_requirements_rejects_duplicate_package() -> None:
    """Reject duplicate dev package declarations."""
    requirements = [
        "black>=24.10,<26; extra == 'dev'",
        "black>=24.10,<26; extra == 'dev'",
        "build>=1.2,<2; extra == 'dev'",
        "mypy>=1.13,<2; extra == 'dev'",
        "pytest>=8.3,<9; extra == 'dev'",
        "pytest-cov>=6,<7; extra == 'dev'",
        "ruff>=0.9,<1; extra == 'dev'",
    ]

    with pytest.raises(verify.DistributionVerificationError, match="duplicates"):
        verify._verify_dev_requirements(requirements, "test metadata")
