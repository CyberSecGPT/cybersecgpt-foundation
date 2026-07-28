"""Tests for repository documentation and security policy validation."""

from pathlib import Path

import pytest
from scripts import validate_repository as policy


def test_repository_policy_accepts_current_repository(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The checked-out repository satisfies its documented policy."""
    policy.main()

    assert "Repository policy validation passed" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("example.py", b"value = 1\n"),
        ("example.cmd", b"@echo off\r\n"),
    ],
)
def test_read_text_accepts_governed_line_endings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    name: str,
    content: bytes,
) -> None:
    """Governed text accepts LF, with CRLF reserved for command files."""
    monkeypatch.setattr(policy, "REPOSITORY_ROOT", tmp_path)
    path = tmp_path / name
    path.write_bytes(content)

    assert policy._read_text(path)


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("example.py", b"value = 1\r\n"),
        ("example.cmd", b"@echo off\n"),
        ("example.py", b"value = 1 \n"),
        ("example.py", b"value = 1"),
        ("example.py", b"\xff\n"),
    ],
)
def test_read_text_rejects_policy_violations(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    name: str,
    content: bytes,
) -> None:
    """Encoding, newline, and trailing-whitespace failures are rejected."""
    monkeypatch.setattr(policy, "REPOSITORY_ROOT", tmp_path)
    path = tmp_path / name
    path.write_bytes(content)

    with pytest.raises(policy.RepositoryValidationError):
        policy._read_text(path)


def test_markdown_prose_excludes_fenced_code() -> None:
    """Governance headings inside code examples do not satisfy policy."""
    markdown = "# Real\n\n```text\n## Not policy\n```\n\n## Actual\n"

    prose = policy._markdown_prose(markdown)

    assert "# Real" in prose
    assert "## Actual" in prose
    assert "## Not policy" not in prose


def test_markdown_anchors_include_duplicate_suffixes() -> None:
    """Repeated headings receive deterministic GitHub-style anchors."""
    markdown = "# Policy\n\n## Review\n\n## Review\n"

    assert policy._markdown_anchors(markdown) == {"policy", "review", "review-1"}


def test_markdown_links_reject_undefined_image_reference(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Reference-style images must define their destination."""
    monkeypatch.setattr(policy, "REPOSITORY_ROOT", tmp_path)
    source = tmp_path / "source.md"
    source.write_text("![diagram][missing]\n", encoding="utf-8", newline="\n")

    with pytest.raises(policy.RepositoryValidationError, match="undefined"):
        policy._validate_markdown_links(
            {Path("source.md"): source.read_text(encoding="utf-8")}
        )


def test_markdown_links_reject_missing_heading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A local Markdown fragment must resolve to an existing heading."""
    monkeypatch.setattr(policy, "REPOSITORY_ROOT", tmp_path)
    source = tmp_path / "source.md"
    target = tmp_path / "target.md"
    source.write_text("[target](target.md#missing)\n", encoding="utf-8", newline="\n")
    target.write_text("# Existing\n", encoding="utf-8", newline="\n")
    text_by_path = {
        Path("source.md"): source.read_text(encoding="utf-8"),
        Path("target.md"): target.read_text(encoding="utf-8"),
    }

    with pytest.raises(policy.RepositoryValidationError, match="heading"):
        policy._validate_markdown_links(text_by_path)


def test_sensitive_material_rejects_environment_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Non-example environment files cannot enter the repository."""
    monkeypatch.setattr(policy, "REPOSITORY_ROOT", tmp_path)
    environment_file = tmp_path / ".env.production"
    environment_file.write_text("MODE=production\n", encoding="utf-8", newline="\n")

    with pytest.raises(policy.RepositoryValidationError, match="environment"):
        policy._validate_sensitive_material([environment_file], {})


@pytest.mark.parametrize(
    "sensitive_text",
    [
        "-----BEGIN " + "PRIVATE KEY-----",
        "AKIA" + ("A" * 16),
        "ASIA" + ("B" * 16),
        "github_" + "pat_" + ("c" * 24),
        "ghp_" + ("d" * 24),
        "xoxb-" + ("e" * 24),
        "client_" + "secret=" + ("f" * 24),
    ],
)
def test_sensitive_material_rejects_secret_patterns(sensitive_text: str) -> None:
    """Representative private keys and access tokens are detected."""
    with pytest.raises(policy.RepositoryValidationError):
        policy._validate_sensitive_material(
            [],
            {Path("sample.txt"): sensitive_text},
        )
