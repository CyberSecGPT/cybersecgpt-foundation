"""Validate documentation integrity and repository security boundaries."""

import hashlib
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

FALLBACK_EXCLUDED_ROOTS = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "build",
        "dist",
        "venv",
    }
)

TEXT_SUFFIXES = frozenset(
    {
        ".bat",
        ".cfg",
        ".cmd",
        ".conf",
        ".ini",
        ".json",
        ".md",
        ".ps1",
        ".py",
        ".sh",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
TEXT_NAMES = frozenset({".env.example", ".gitattributes", ".gitignore", "LICENSE"})

REQUIRED_HEADINGS = {
    "README.md": frozenset(
        {
            "# cybersecgpt-foundation",
            "## Responsibilities",
            "## Excluded responsibilities",
            "## Edition positioning",
            "## Founder and Maintainers",
            "## Architecture governance",
            "## License",
        }
    ),
    "CONTRIBUTING.md": frozenset(
        {
            "# Contributing to cybersecgpt-foundation",
            "## Branch naming",
            "## Development setup",
            "## Test requirements",
            "## Linting, formatting, and type checking",
            "## Edition and feature placement",
            "## Architecture governance",
            "## Pull request expectations",
            "## Contributor License Agreement and licensing",
            "## Dependency governance",
            "## Release and exception governance",
            "## Conventional commits",
        }
    ),
    "SECURITY.md": frozenset(
        {
            "# Security Policy",
            "## Reporting a vulnerability",
            "## Information to include",
            "## Supported versions",
            "## Responsible disclosure",
        }
    ),
    "CHANGELOG.md": frozenset({"# Changelog", "## Unreleased"}),
    "docs/ARCHITECTURE.md": frozenset(
        {
            "# cybersecgpt-foundation Architecture",
            "## Status and governance",
            "## Role in the platform",
            "## Edition boundary",
            "## Scope",
            "## Internal dependency direction",
            "## Quality gates",
        }
    ),
    "docs/EDITION_MATRIX.md": frozenset(
        {
            "# CyberSecGPT Foundation Edition Matrix",
            "## Status",
            "## Availability",
            "## Repository boundary",
            "## Upgrade, downgrade, and data behavior",
            "## Change control",
        }
    ),
}

REQUIRED_PHRASES = {
    "README.md": frozenset(
        {
            "**Repository lifecycle: Bootstrap.**",
            "`cybersecgpt-foundation` is shared Community-layer infrastructure.",
            "This repository contains no premium",
            "The CyberSecGPT Founder retains final authority",
            "The CyberSecGPT Chief Architect is responsible",
            "The CyberSecGPT Team maintains `cybersecgpt-foundation`.",
            "source-available licensing model",
            "CyberSecGPT Community Source License (CSL) Version 1.0",
            "cybersecgpt-docs",
        }
    ),
    "CONTRIBUTING.md": frozenset(
        {
            "The `main`, `release/*`, and `hotfix/*` branches are protected.",
            "Architecture Decision Record",
            "maintenance activity",
            "supply-chain risk",
            "Every pull request requires review before merge.",
            "agents must not approve their own changes.",
            "Reviewers evaluate correctness, readability, maintainability, security,",
            "External contributors must accept the CyberSecGPT Contributor",
            "Community Source License (CSL) Version 1.0",
            "Keep authorization separate from commercial entitlement decisions.",
            "Only repository maintainers may approve a release.",
            "Permanent exceptions require Founder approval.",
        }
    ),
    "SECURITY.md": frozenset(
        {
            "Do not report an undisclosed vulnerability in a public issue",
            "private vulnerability reporting form",
            "has no public release",
            "Public issues must never contain details of an undisclosed vulnerability.",
        }
    ),
    "CHANGELOG.md": frozenset(
        {
            "## Unreleased",
            "CyberSecGPT Community",
            "distribution-boundary",
        }
    ),
    "docs/ARCHITECTURE.md": frozenset(
        {
            "Architecture Decision Record",
            "Dependency flow in the opposite direction is prohibited.",
            "entitlement separate from",
            "no runtime dependency on another",
            "repository documentation and local-link validation",
            "distribution content, dependency, edition-boundary, and license-metadata",
        }
    ),
    "docs/EDITION_MATRIX.md": frozenset(
        {
            "`Included`",
            "`Limited`",
            "`Add-on`",
            "`Preview`",
            "`Deprecated`",
            "`Not available`",
            "| Foundation capability | Community | Professional | Enterprise |",
            "lower editions must not depend on",
            "Every new capability must be classified before implementation.",
            "Significant placement decisions require approval",
        }
    ),
}

EXPECTED_LICENSE_SHA256 = (
    "1871f215d0ee4286c29a8dcb5e4905ccedda0f8d69bb79b8a4441e30417e1e38"
)

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
REFERENCE_DEFINITION = re.compile(
    r"^[ \t]{0,3}\[([^\]]+)\]:[ \t]*(?:<([^>]+)>|(\S+))",
    re.MULTILINE,
)
REFERENCE_USAGE = re.compile(r"\[([^\]\n]+)]\[([^\]\n]*)]")
MARKDOWN_HEADING = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
EXTERNAL_LINK = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

SENSITIVE_FILE_NAMES = frozenset(
    {
        ".env",
        "credentials.json",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
        "service-account.json",
    }
)
SENSITIVE_FILE_SUFFIXES = frozenset({".jks", ".key", ".p12", ".pfx", ".pem"})

SENSITIVE_CONTENT_PATTERNS = (
    (
        "private key material",
        re.compile(
            re.escape("-----BEGIN ")
            + r"(?:DSA |EC |OPENSSH |PGP |RSA )?"
            + re.escape("PRIVATE KEY")
            + r"(?: BLOCK)?"
            + re.escape("-----")
        ),
    ),
    ("cloud access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (
        "GitHub access token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "GitHub fine-grained access token",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    ),
    (
        "Slack access token",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    ),
    (
        "assigned secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|client[_-]?secret|password|token)\b"
            r"\s*[:=]\s*[\"']?[A-Za-z0-9/+_.=-]{16,}"
        ),
    ),
)


class RepositoryValidationError(RuntimeError):
    """Report a repository policy violation."""


def _require(condition: bool, message: str) -> None:
    """Raise a policy error when a required condition is not satisfied."""
    if not condition:
        raise RepositoryValidationError(message)


def _repository_files() -> list[Path]:
    """Return tracked and non-ignored files, including tracked generated paths."""
    git_metadata = REPOSITORY_ROOT / ".git"
    if git_metadata.exists():
        try:
            result = subprocess.run(
                [
                    "git",
                    "ls-files",
                    "-z",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                ],
                cwd=REPOSITORY_ROOT,
                check=True,
                capture_output=True,
                encoding="utf-8",
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise RepositoryValidationError(
                "unable to enumerate repository files with Git"
            ) from error

        paths: list[Path] = []
        for relative_name in result.stdout.split("\0"):
            if not relative_name:
                continue
            path = (REPOSITORY_ROOT / relative_name).resolve()
            _require(
                path.is_relative_to(REPOSITORY_ROOT.resolve()),
                f"Git returned a path outside the repository: {relative_name}",
            )
            _require(
                path.is_file(),
                f"listed repository file is missing: {relative_name}",
            )
            paths.append(path)

        environment_files = [
            path.resolve()
            for path in REPOSITORY_ROOT.rglob(".env*")
            if path.is_file() and ".git" not in path.parts
        ]
        return sorted(set(paths) | set(environment_files))

    return [
        path
        for path in sorted(REPOSITORY_ROOT.rglob("*"))
        if path.is_file()
        and path.relative_to(REPOSITORY_ROOT).parts[0] not in FALLBACK_EXCLUDED_ROOTS
        and "__pycache__" not in path.parts
    ]


def _is_text_file(path: Path) -> bool:
    """Return whether a repository file is governed as UTF-8 text."""
    return path.suffix.casefold() in TEXT_SUFFIXES or path.name in TEXT_NAMES


def _read_text(path: Path) -> str:
    """Read strict UTF-8 text and enforce repository whitespace policy."""
    content = path.read_bytes()
    relative_path = path.relative_to(REPOSITORY_ROOT)
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RepositoryValidationError(
            f"text file is not valid UTF-8: {relative_path}"
        ) from error
    if path.suffix.casefold() in {".bat", ".cmd"}:
        content_without_crlf = content.replace(b"\r\n", b"")
        _require(
            b"\r" not in content_without_crlf and b"\n" not in content_without_crlf,
            f"Windows command file does not use CRLF endings: {relative_path}",
        )
        _require(
            not content or content.endswith(b"\r\n"),
            f"text file has no final newline: {relative_path}",
        )
    else:
        _require(
            b"\r" not in content,
            f"text file does not use LF endings: {relative_path}",
        )
        _require(
            not content or content.endswith(b"\n"),
            f"text file has no final newline: {relative_path}",
        )
    for line_number, line in enumerate(text.splitlines(), start=1):
        _require(
            not line.endswith((" ", "\t")),
            f"text file has trailing whitespace: {relative_path}:{line_number}",
        )
    return text


def _markdown_prose(text: str) -> str:
    """Remove fenced code blocks from Markdown policy validation."""
    prose_lines: list[str] = []
    active_fence: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        fence = stripped[:3]
        if fence in {"```", "~~~"}:
            if active_fence is None:
                active_fence = fence
            elif active_fence == fence:
                active_fence = None
            continue
        if active_fence is None:
            prose_lines.append(line)
    return "\n".join(prose_lines)


def _validate_required_documentation(text_by_path: dict[Path, str]) -> None:
    """Verify required documents, governance sections, and policy content."""
    for relative_name, required_headings in REQUIRED_HEADINGS.items():
        relative_path = Path(relative_name)
        _require(
            relative_path in text_by_path,
            f"required documentation is missing: {relative_name}",
        )
        prose = _markdown_prose(text_by_path[relative_path])
        headings = set(prose.splitlines())
        missing = sorted(required_headings - headings)
        _require(
            not missing,
            f"{relative_name} is missing required headings: {missing}",
        )
        missing_phrases = sorted(
            phrase for phrase in REQUIRED_PHRASES[relative_name] if phrase not in prose
        )
        _require(
            not missing_phrases,
            f"{relative_name} is missing policy content: {missing_phrases}",
        )

    license_path = Path("LICENSE")
    _require(license_path in text_by_path, "required licensing notice is missing")
    license_digest = hashlib.sha256(
        text_by_path[license_path].encode("utf-8")
    ).hexdigest()
    _require(
        license_digest == EXPECTED_LICENSE_SHA256,
        "licensing notice differs from the owner-approved pending notice",
    )


def _reference_label(text: str) -> str:
    """Normalize a Markdown reference label."""
    return " ".join(text.casefold().split())


def _markdown_anchors(text: str) -> set[str]:
    """Return GitHub-style heading anchors for a Markdown document."""
    anchors: set[str] = set()
    occurrences: dict[str, int] = {}
    for line in _markdown_prose(text).splitlines():
        match = MARKDOWN_HEADING.match(line)
        if match is None:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1))
        heading = re.sub(r"!\[([^\]]*)]\([^)]+\)", r"\1", heading)
        heading = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", heading)
        heading = heading.replace("`", "").replace("*", "").replace("_", "")
        base = re.sub(r"[^\w\s-]", "", heading.casefold())
        base = re.sub(r"\s+", "-", base.strip())
        if not base:
            continue
        occurrence = occurrences.get(base, 0)
        anchor = base if occurrence == 0 else f"{base}-{occurrence}"
        occurrences[base] = occurrence + 1
        anchors.add(anchor)
    return anchors


def _link_target(raw_destination: str) -> str:
    """Extract a Markdown destination without an optional title."""
    destination = raw_destination.strip()
    if destination.startswith("<"):
        closing = destination.find(">")
        _require(closing > 1, f"malformed angle-bracket link: {raw_destination}")
        return destination[1:closing]
    return destination.split(maxsplit=1)[0] if destination else ""


def _validate_link_destination(
    relative_path: Path,
    raw_destination: str,
    text_by_path: dict[Path, str],
) -> None:
    """Verify a single repository-relative link and Markdown fragment."""
    destination = unquote(_link_target(raw_destination))
    _require(bool(destination), f"{relative_path} contains an empty link")
    if EXTERNAL_LINK.match(destination):
        return

    path_text, separator, fragment = destination.partition("#")
    linked_path = (
        (REPOSITORY_ROOT / relative_path.parent / path_text).resolve()
        if path_text
        else (REPOSITORY_ROOT / relative_path).resolve()
    )
    repository_root = REPOSITORY_ROOT.resolve()
    _require(
        linked_path.is_relative_to(repository_root),
        f"{relative_path} links outside the repository: {destination}",
    )
    _require(
        linked_path.is_file(),
        f"{relative_path} contains a broken local link: {destination}",
    )

    if separator and fragment and linked_path.suffix.casefold() == ".md":
        linked_relative_path = linked_path.relative_to(repository_root)
        linked_text = text_by_path.get(linked_relative_path)
        if linked_text is None:
            raise RepositoryValidationError(
                f"linked Markdown file is not governed text: {linked_relative_path}"
            )
        _require(
            fragment.casefold() in _markdown_anchors(linked_text),
            f"{relative_path} contains a broken heading link: {destination}",
        )


def _validate_markdown_links(text_by_path: dict[Path, str]) -> None:
    """Verify inline and reference-style local Markdown links and fragments."""
    for relative_path, text in text_by_path.items():
        if relative_path.suffix.casefold() != ".md":
            continue
        prose = _markdown_prose(text)
        for match in MARKDOWN_LINK.finditer(prose):
            _validate_link_destination(relative_path, match.group(1), text_by_path)

        definitions: dict[str, str] = {}
        for match in REFERENCE_DEFINITION.finditer(prose):
            label = _reference_label(match.group(1))
            destination = match.group(2) or match.group(3)
            _require(
                label not in definitions,
                f"{relative_path} contains a duplicate link reference: {label}",
            )
            definitions[label] = destination
            _validate_link_destination(relative_path, destination, text_by_path)

        for match in REFERENCE_USAGE.finditer(prose):
            label_text = match.group(2) or match.group(1)
            label = _reference_label(label_text)
            _require(
                label in definitions,
                f"{relative_path} uses an undefined link reference: {label_text}",
            )


def _validate_sensitive_material(
    repository_files: list[Path],
    text_by_path: dict[Path, str],
) -> None:
    """Reject common credential files, private keys, and access tokens."""
    for path in repository_files:
        relative_path = path.relative_to(REPOSITORY_ROOT)
        file_name = path.name.casefold()
        _require(
            file_name not in SENSITIVE_FILE_NAMES,
            f"repository contains a sensitive file: {relative_path}",
        )
        _require(
            not file_name.startswith(".env") or file_name == ".env.example",
            f"repository contains a non-example environment file: {relative_path}",
        )
        _require(
            path.suffix.casefold() not in SENSITIVE_FILE_SUFFIXES,
            f"repository contains a sensitive file type: {relative_path}",
        )

    for relative_path, text in text_by_path.items():
        for description, pattern in SENSITIVE_CONTENT_PATTERNS:
            _require(
                pattern.search(text) is None,
                f"{relative_path} contains {description}",
            )


def main() -> None:
    """Run documentation, encoding, link, and sensitive-material checks."""
    repository_files = _repository_files()
    text_by_path = {
        path.relative_to(REPOSITORY_ROOT): _read_text(path)
        for path in repository_files
        if _is_text_file(path)
    }
    _validate_required_documentation(text_by_path)
    _validate_markdown_links(text_by_path)
    _validate_sensitive_material(repository_files, text_by_path)
    print(
        "Repository policy validation passed for "
        f"{len(text_by_path)} text files and {len(REQUIRED_HEADINGS)} documents."
    )


if __name__ == "__main__":
    main()
