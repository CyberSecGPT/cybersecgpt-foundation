"""Verify that built distributions preserve the shared foundation boundary."""

import argparse
import base64
import csv
import hashlib
import io
import re
import stat
import tarfile
import warnings
import zipfile
from email.message import Message
from email.parser import Parser
from pathlib import Path, PurePosixPath

EXPECTED_NAME = "cybersecgpt-foundation"
EXPECTED_NORMALIZED_NAME = "cybersecgpt_foundation"
EXPECTED_VERSION = "0.1.0"
EXPECTED_SUMMARY = "Shared foundation library for the CyberSecGPT platform."
EXPECTED_REQUIRES_PYTHON = ">=3.11"
EXPECTED_LICENSE_EXPRESSION = "LicenseRef-CyberSecGPT-CSL-1.0"
EXPECTED_AUTHOR = "CyberSecGPT Team"
EXPECTED_KEYWORDS = "AI,LLM,cybersecurity,framework,security"
EXPECTED_WHEEL_TAG = "py3-none-any"
EXPECTED_WHEEL_FILENAME = (
    f"{EXPECTED_NORMALIZED_NAME}-{EXPECTED_VERSION}-{EXPECTED_WHEEL_TAG}.whl"
)
EXPECTED_SDIST_ROOT = f"{EXPECTED_NORMALIZED_NAME}-{EXPECTED_VERSION}"
EXPECTED_SDIST_FILENAME = f"{EXPECTED_SDIST_ROOT}.tar.gz"
EXPECTED_DIST_INFO = f"{EXPECTED_NORMALIZED_NAME}-{EXPECTED_VERSION}.dist-info"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

_MIN_METADATA_VERSION = (2, 4)
_HIGHEST_KNOWN_METADATA_VERSION = (2, 5)
_SUPPORTED_METADATA_MAJOR = 2

EXPECTED_CLASSIFIERS = frozenset(
    {
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    }
)

EXPECTED_DEV_PACKAGES = frozenset(
    {
        "black",
        "build",
        "mypy",
        "pytest",
        "pytest-cov",
        "ruff",
    }
)
_VERSION_SPECIFIER_START = frozenset("<>=!")

EXPECTED_PACKAGE_FILES = frozenset(
    {
        "cybersecgpt/__init__.py",
        "cybersecgpt/foundation/__init__.py",
        "cybersecgpt/foundation/constants.py",
        "cybersecgpt/foundation/exceptions.py",
        "cybersecgpt/foundation/identifiers.py",
        "cybersecgpt/foundation/logging.py",
        "cybersecgpt/foundation/serialization.py",
        "cybersecgpt/foundation/security/__init__.py",
        "cybersecgpt/foundation/security/audit.py",
        "cybersecgpt/foundation/security/context.py",
        "cybersecgpt/foundation/security/evidence.py",
        "cybersecgpt/foundation/typing.py",
        "cybersecgpt/foundation/utils.py",
        "cybersecgpt/foundation/validation.py",
        "cybersecgpt/foundation/version.py",
    }
)

EXPECTED_TEST_FILES = frozenset(
    {
        "tests/__init__.py",
        "tests/test_constants.py",
        "tests/test_exceptions.py",
        "tests/test_identifiers.py",
        "tests/test_logging.py",
        "tests/test_repository_policy.py",
        "tests/test_security_audit.py",
        "tests/test_security_context.py",
        "tests/test_security_evidence.py",
        "tests/test_serialization.py",
        "tests/test_typing.py",
        "tests/test_utils.py",
        "tests/test_validation.py",
        "tests/test_verify_distribution.py",
        "tests/test_version.py",
    }
)

EXPECTED_REPOSITORY_FILES = frozenset(
    {
        ".gitattributes",
        ".github/workflows/ci.yml",
        ".gitignore",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "README.md",
        "SECURITY.md",
        "docs/ARCHITECTURE.md",
        "docs/EDITION_MATRIX.md",
        "pyproject.toml",
        "scripts/validate_repository.py",
        "scripts/verify_distribution.py",
    }
)

EXPECTED_SDIST_FILES = (
    EXPECTED_REPOSITORY_FILES
    | EXPECTED_TEST_FILES
    | {f"src/{name}" for name in EXPECTED_PACKAGE_FILES}
    | {"PKG-INFO"}
)


class DistributionVerificationError(RuntimeError):
    """Report a distribution that violates repository packaging policy."""


def _require(condition: bool, message: str) -> None:
    """Raise a policy error when a required condition is not satisfied."""
    if not condition:
        raise DistributionVerificationError(message)


def _single_path(paths: list[Path], description: str) -> Path:
    """Return the only matching path in a distribution directory."""
    _require(len(paths) == 1, f"expected one {description}, found {len(paths)}")
    return paths[0]


def _header_values(message: Message, name: str) -> list[str]:
    """Return every value for a metadata header as plain text."""
    return [str(value) for value in message.get_all(name, [])]


def _verify_single_header(
    message: Message,
    name: str,
    expected: str,
    source: str,
) -> None:
    """Verify a metadata header occurs once with the expected value."""
    actual = _header_values(message, name)
    _require(
        actual == [expected],
        f"{source} {name} is incorrect: expected {expected!r}, found {actual!r}",
    )


def _parse_metadata(content: bytes, source: str) -> Message:
    """Parse UTF-8 package metadata."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DistributionVerificationError(f"{source} is not valid UTF-8") from error
    return Parser().parsestr(text)


def _parse_metadata_version(value: str) -> tuple[int, int]:
    """Parse a Core Metadata version string into ``(major, minor)``."""
    parts = value.split(".")
    if len(parts) != 2:
        raise DistributionVerificationError(f"malformed Metadata-Version: {value!r}")
    try:
        major = int(parts[0])
        minor = int(parts[1])
    except ValueError as error:
        raise DistributionVerificationError(
            f"malformed Metadata-Version: {value!r}"
        ) from error
    return major, minor


def _verify_metadata_version(metadata: Message, source: str) -> None:
    """Verify Core Metadata version compatibility for this project."""
    values = _header_values(metadata, "Metadata-Version")
    _require(
        len(values) == 1,
        f"{source} Metadata-Version must occur once, found {len(values)}",
    )
    version_text = values[0]
    major, minor = _parse_metadata_version(version_text)
    parsed = (major, minor)
    _require(
        major <= _SUPPORTED_METADATA_MAJOR,
        f"{source} unsupported Metadata-Version major: {version_text}",
    )
    _require(
        parsed >= _MIN_METADATA_VERSION,
        f"{source} Metadata-Version must be at least "
        f"{_MIN_METADATA_VERSION[0]}.{_MIN_METADATA_VERSION[1]}, "
        f"found {version_text}",
    )
    if parsed > _HIGHEST_KNOWN_METADATA_VERSION:
        warnings.warn(
            f"{source} Metadata-Version {version_text} is newer than the highest "
            f"known version {_HIGHEST_KNOWN_METADATA_VERSION[0]}."
            f"{_HIGHEST_KNOWN_METADATA_VERSION[1]}; verification accepted "
            "under PEP core-metadata major-version rules",
            stacklevel=2,
        )


def _is_dev_extra_marker(marker: str) -> bool:
    """Return whether a Requires-Dist marker targets the dev extra."""
    return marker.replace('"', "'") == "extra == 'dev'"


def _dev_package_name(specification: str) -> str | None:
    """Extract a known dev package name from a constrained Requires-Dist spec."""
    for package in EXPECTED_DEV_PACKAGES:
        if specification == package:
            return package
        if not specification.startswith(package):
            continue
        if len(specification) == len(package):
            return package
        next_character = specification[len(package)]
        if next_character in _VERSION_SPECIFIER_START:
            return package
    return None


def _parse_dev_requires_dist(requirement: str) -> str | None:
    """Extract the package name from this project's dev-extra metadata."""
    requirement_part, separator, marker = requirement.partition(";")

    if not separator:
        return None

    normalized_marker = marker.replace('"', "'").replace(" ", "")

    if normalized_marker != "extra=='dev'":
        return None

    requirement_part = requirement_part.strip()

    _require(
        bool(requirement_part),
        f"invalid dev Requires-Dist entry: {requirement!r}",
    )

    operator_positions = [
        requirement_part.find(character)
        for character in "<>!=~"
        if requirement_part.find(character) >= 0
    ]

    if operator_positions:
        package_name = requirement_part[: min(operator_positions)].strip()
    else:
        package_name = requirement_part

    _require(
        bool(package_name),
        f"missing package name in Requires-Dist entry: {requirement!r}",
    )

    _require(
        all(character.isalnum() or character in "-_." for character in package_name),
        f"invalid package name in Requires-Dist entry: {requirement!r}",
    )

    return re.sub(r"[-_.]+", "-", package_name).lower()


def _verify_dev_requirements(requirements: list[str], source: str) -> None:
    """Verify that the dev extra contains exactly the expected packages."""
    dev_packages: list[str] = []

    for requirement in requirements:
        package_name = _parse_dev_requires_dist(requirement)

        if package_name is not None:
            dev_packages.append(package_name)

    duplicates = sorted(
        {package for package in dev_packages if dev_packages.count(package) > 1}
    )

    _require(
        not duplicates,
        f"{source} dev dependencies contain duplicates: {duplicates}",
    )

    actual_packages = set(dev_packages)

    missing = sorted(EXPECTED_DEV_PACKAGES - actual_packages)
    unexpected = sorted(actual_packages - EXPECTED_DEV_PACKAGES)

    _require(
        not missing and not unexpected,
        (
            f"{source} dev dependency set is incorrect: "
            f"missing={missing}, unexpected={unexpected}"
        ),
    )

    _require(
        len(dev_packages) == len(EXPECTED_DEV_PACKAGES),
        (f"{source} dev dependency count is incorrect: " f"{dev_packages}"),
    )


def _verify_project_metadata(content: bytes, source: str) -> None:
    """Verify core, dependency, Python, and license metadata."""
    metadata = _parse_metadata(content, source)
    _verify_metadata_version(metadata, source)
    expected_headers = {
        "Name": EXPECTED_NAME,
        "Version": EXPECTED_VERSION,
        "Summary": EXPECTED_SUMMARY,
        "Requires-Python": EXPECTED_REQUIRES_PYTHON,
        "License-Expression": EXPECTED_LICENSE_EXPRESSION,
        "Author": EXPECTED_AUTHOR,
        "Keywords": EXPECTED_KEYWORDS,
        "Provides-Extra": "dev",
    }
    for name, expected in expected_headers.items():
        _verify_single_header(metadata, name, expected, source)

    _require(
        not _header_values(metadata, "License"),
        f"{source} uses a legacy license field",
    )
    _require(
        _header_values(metadata, "License-File") == ["LICENSE"],
        f"{source} license-file metadata is incorrect",
    )

    classifiers = _header_values(metadata, "Classifier")
    _require(
        len(classifiers) == len(EXPECTED_CLASSIFIERS)
        and set(classifiers) == EXPECTED_CLASSIFIERS,
        f"{source} classifiers are incorrect: {classifiers}",
    )

    requirements = _header_values(metadata, "Requires-Dist")
    _require(
        len(requirements) == len(EXPECTED_DEV_PACKAGES),
        f"{source} dependency metadata count is incorrect: {requirements}",
    )
    _verify_dev_requirements(requirements, source)


def _verify_archive_names(names: list[str], source: str) -> None:
    """Reject duplicate, absolute, non-canonical, or traversing members."""
    _require(
        len(names) == len(set(names)),
        f"{source} contains duplicate archive members",
    )
    normalized_names = [name.rstrip("/") for name in names]
    _require(
        len(normalized_names) == len(set(normalized_names)),
        f"{source} contains ambiguous file and directory members",
    )

    for name in names:
        normalized_name = name.rstrip("/")
        path = PurePosixPath(normalized_name)
        _require(bool(normalized_name), f"{source} contains an empty member name")
        _require("\\" not in name, f"{source} contains a backslash path: {name}")
        _require(not path.is_absolute(), f"{source} contains an absolute path: {name}")
        _require(
            all(part not in {".", ".."} for part in path.parts),
            f"{source} contains a traversing path: {name}",
        )
        _require(
            str(path) == normalized_name,
            f"{source} contains a non-canonical path: {name}",
        )


def _repository_bytes(relative_path: str) -> bytes:
    """Read an expected repository file without path ambiguity."""
    path = REPOSITORY_ROOT / PurePosixPath(relative_path)
    _require(path.is_file(), f"repository file is missing: {relative_path}")
    return path.read_bytes()


def _verify_repository_copy(
    content: bytes,
    relative_path: str,
    source: str,
) -> None:
    """Verify that an archive contains the repository file byte-for-byte."""
    _require(
        content == _repository_bytes(relative_path),
        f"{source} does not match repository file {relative_path}",
    )


def _verify_wheel_record(
    archive: zipfile.ZipFile,
    names: set[str],
    record_member: str,
) -> None:
    """Verify RECORD coverage, hashes, and sizes for every wheel member."""
    record_text = archive.read(record_member).decode("utf-8")
    rows = list(csv.reader(io.StringIO(record_text)))
    _require(
        all(len(row) == 3 for row in rows),
        "wheel RECORD contains malformed rows",
    )
    record_names = [row[0] for row in rows]
    _require(
        len(record_names) == len(set(record_names)),
        "wheel RECORD contains duplicate entries",
    )
    _require(set(record_names) == names, "wheel RECORD member list is incorrect")

    for member_name, digest, size in rows:
        if member_name == record_member:
            _require(
                not digest and not size,
                "wheel RECORD must not hash or size itself",
            )
            continue

        content = archive.read(member_name)
        encoded_digest = base64.urlsafe_b64encode(
            hashlib.sha256(content).digest()
        ).rstrip(b"=")
        expected_digest = f"sha256={encoded_digest.decode('ascii')}"
        _require(
            digest == expected_digest,
            f"wheel RECORD hash is incorrect for {member_name}",
        )
        _require(
            size == str(len(content)),
            f"wheel RECORD size is incorrect for {member_name}",
        )


def verify_wheel(path: Path) -> None:
    """Verify wheel contents, dependency boundaries, and license metadata."""
    _require(
        path.name == EXPECTED_WHEEL_FILENAME,
        f"wheel filename is incorrect: {path.name}",
    )
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        member_names = [member.filename for member in members]
        _verify_archive_names(member_names, "wheel")
        for member in members:
            _require(
                not member.is_dir(),
                f"wheel contains a directory: {member.filename}",
            )
            file_type = stat.S_IFMT(member.external_attr >> 16)
            _require(
                file_type in {0, stat.S_IFREG},
                f"wheel contains a non-regular file: {member.filename}",
            )
            _require(
                not member.flag_bits & 0x1,
                f"wheel contains an encrypted file: {member.filename}",
            )

        names = set(member_names)
        metadata_member = f"{EXPECTED_DIST_INFO}/METADATA"
        wheel_member = f"{EXPECTED_DIST_INFO}/WHEEL"
        license_member = f"{EXPECTED_DIST_INFO}/licenses/LICENSE"
        record_member = f"{EXPECTED_DIST_INFO}/RECORD"
        expected_names = EXPECTED_PACKAGE_FILES | {
            metadata_member,
            wheel_member,
            license_member,
            record_member,
        }
        unexpected = sorted(names - expected_names)
        missing = sorted(expected_names - names)
        _require(not unexpected, f"wheel contains unexpected files: {unexpected}")
        _require(not missing, f"wheel is missing required files: {missing}")

        _verify_project_metadata(archive.read(metadata_member), "wheel metadata")

        wheel_metadata = _parse_metadata(archive.read(wheel_member), "WHEEL")
        _verify_single_header(wheel_metadata, "Wheel-Version", "1.0", "WHEEL")
        _verify_single_header(wheel_metadata, "Root-Is-Purelib", "true", "WHEEL")
        _require(
            _header_values(wheel_metadata, "Tag") == [EXPECTED_WHEEL_TAG],
            "WHEEL tag is incorrect",
        )
        _require(
            not _header_values(wheel_metadata, "Build"),
            "WHEEL contains an unexpected build tag",
        )

        _verify_repository_copy(
            archive.read(license_member),
            "LICENSE",
            "wheel license",
        )
        for package_file in EXPECTED_PACKAGE_FILES:
            _verify_repository_copy(
                archive.read(package_file),
                f"src/{package_file}",
                f"wheel member {package_file}",
            )
        _verify_wheel_record(archive, names, record_member)


def verify_sdist(path: Path) -> None:
    """Verify source archive contents and shared-package boundaries."""
    _require(
        path.name == EXPECTED_SDIST_FILENAME,
        f"source archive filename is incorrect: {path.name}",
    )
    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()
        member_names = [member.name for member in members]
        _verify_archive_names(member_names, "source archive")
        for member in members:
            _require(
                member.isfile() or member.isdir(),
                f"source archive contains a non-regular member: {member.name}",
            )

        roots = {PurePosixPath(name.rstrip("/")).parts[0] for name in member_names}
        _require(
            roots == {EXPECTED_SDIST_ROOT},
            f"source archive has unexpected roots: {sorted(roots)}",
        )
        file_names = {member.name for member in members if member.isfile()}
        relative_names = {
            str(PurePosixPath(name).relative_to(EXPECTED_SDIST_ROOT))
            for name in file_names
        }

        unexpected = sorted(relative_names - EXPECTED_SDIST_FILES)
        missing = sorted(EXPECTED_SDIST_FILES - relative_names)
        _require(
            not unexpected,
            f"source archive contains unexpected files: {unexpected}",
        )
        _require(not missing, f"source archive is missing required files: {missing}")

        archive_files: dict[str, bytes] = {}
        for relative_name in relative_names:
            member_name = f"{EXPECTED_SDIST_ROOT}/{relative_name}"
            extracted_file = archive.extractfile(member_name)
            if extracted_file is None:
                raise DistributionVerificationError(
                    f"source archive member is unreadable: {relative_name}"
                )
            archive_files[relative_name] = extracted_file.read()

        _verify_project_metadata(
            archive_files["PKG-INFO"],
            "source archive metadata",
        )
        for relative_name in EXPECTED_SDIST_FILES - {"PKG-INFO"}:
            _verify_repository_copy(
                archive_files[relative_name],
                relative_name,
                f"source archive member {relative_name}",
            )


def main() -> None:
    """Verify the single wheel and source archive in a build directory."""
    parser = argparse.ArgumentParser(
        description="Verify CyberSecGPT foundation distribution boundaries."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path("dist"),
        help="directory containing one wheel and one source archive",
    )
    args = parser.parse_args()
    directory: Path = args.directory
    _require(directory.is_dir(), f"distribution directory does not exist: {directory}")

    wheel = _single_path(sorted(directory.glob("*.whl")), "wheel")
    sdist = _single_path(sorted(directory.glob("*.tar.gz")), "source archive")
    verify_wheel(wheel)
    verify_sdist(sdist)
    print(f"Verified distribution boundaries for {wheel.name} and {sdist.name}.")


if __name__ == "__main__":
    main()
