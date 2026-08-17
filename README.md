# cybersecgpt-foundation

**Project status: Alpha (0.1.0).** The package is under active development.
Public APIs may change before a stable release.

**Repository lifecycle: Bootstrap.** No public release has been approved.

`cybersecgpt-foundation` is the dependency-light shared Python foundation for
the CyberSecGPT platform. It provides a common home for cross-cutting contracts
and primitives that can be reused without depending on another CyberSecGPT
repository.

## Responsibilities

This repository is responsible for:

- Package and version metadata.
- Shared constants, identifiers, exception vocabulary, and type definitions.
- Common boundaries for validation, logging, serialization, and general
  utilities.
- Strictly typed, independently testable Python interfaces.
- A small and stable dependency surface for downstream CyberSecGPT components.

The `0.1.0` bootstrap exposes version metadata and a deliberately small set of
implemented primitives. New behavior is introduced only with clear ownership,
tests, and an approved architectural need.

## Excluded responsibilities

This repository does not own:

- Cybersecurity product logic such as scanning, detection, remediation, or
  policy enforcement.
- Model training, inference, evaluation, prompting, or dataset processing.
- API services, command-line interfaces, desktop applications, or web
  interfaces.
- Persistence, orchestration, deployment, monitoring, or infrastructure.
- Cross-repository architecture governance.
- Runtime dependencies on other CyberSecGPT repositories.

Those concerns belong in their dedicated repositories.

## Implemented primitives

The current foundation API provides:

- A shared exception hierarchy rooted at `FoundationError`.
- Immutable typed identifiers with UUID4 generation.
- Immutable `SecurityContext` for opaque actor and trace identity.
- Immutable audit-event contracts for structured security-relevant records.
- String and integer validation helpers.
- Deterministic JSON serialization and deserialization.
- Idempotent, opt-in logging configuration and validated logger lookup.
- Timezone-aware UTC datetime and ISO 8601 helpers.
- Stable project constants and recursive JSON-compatible typing aliases.

These primitives use only the Python standard library and remain intentionally
independent of application frameworks and other CyberSecGPT repositories.

## Edition positioning

`cybersecgpt-foundation` is shared Community-layer infrastructure. Its public
primitives are available to Community and may be consumed unchanged by
Professional and Enterprise extensions. This repository contains no premium
feature implementation, entitlement enforcement, or edition-specific business
logic.

The version-controlled availability record is
[docs/EDITION_MATRIX.md](docs/EDITION_MATRIX.md). Feature placement requires
product-governance approval before implementation; it is not decided through
scattered edition checks in foundation code.

## Development installation

Python 3.11 or newer is required.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Linux or macOS
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Install the package and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quality checks

Run the test suite with coverage:

```bash
python -m pytest --cov=cybersecgpt --cov-report=term-missing --cov-fail-under=100
```

Run linting:

```bash
python -m ruff check .
```

Check formatting:

```bash
python -m black --check .
```

Apply formatting:

```bash
python -m black .
```

Run strict type checking:

```bash
python -m mypy src scripts
```

Validate documentation and repository security boundaries:

```bash
python scripts/validate_repository.py
python -m pip check
```

Build the distribution artifacts:

```bash
python -m build
python scripts/verify_distribution.py dist
```

## Package structure

```text
docs/
├── ARCHITECTURE.md
└── EDITION_MATRIX.md
scripts/
├── validate_repository.py
└── verify_distribution.py
src/
└── cybersecgpt/
    ├── __init__.py
    └── foundation/
        ├── __init__.py
        ├── constants.py
        ├── exceptions.py
        ├── identifiers.py
        ├── logging.py
        ├── security/
        │   ├── __init__.py
        │   ├── audit.py
        │   └── context.py
        ├── serialization.py
        ├── typing.py
        ├── utils.py
        ├── validation.py
        └── version.py
tests/
├── test_constants.py
├── test_exceptions.py
├── test_identifiers.py
├── test_logging.py
├── test_repository_policy.py
├── test_security_audit.py
├── test_security_context.py
├── test_serialization.py
├── test_typing.py
├── test_utils.py
├── test_validation.py
├── test_verify_distribution.py
└── test_version.py
```

The top-level `cybersecgpt` package and the `cybersecgpt.foundation` package
both expose the package version.

## Founder and Maintainers

### Founder

The CyberSecGPT Founder retains final authority over the project vision,
architectural direction, licensing strategy, and commercial direction.

### Chief Architect

The CyberSecGPT Chief Architect is responsible for architecture consistency,
technical direction, engineering quality, and coordination across
repositories.

### Maintainers

The CyberSecGPT Team maintains `cybersecgpt-foundation`. Repository maintainers
are responsible for technical review, quality gates, documentation health,
security coordination, and release approval. Changes reach protected branches
only through the governed review process.

## Architecture governance

Repository-level architecture is documented in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Cross-repository architecture, architectural decisions, dependency direction,
and platform-level contracts are governed in
[`cybersecgpt-docs`](https://github.com/CyberSecGPT/cybersecgpt-docs).

Changes in this repository that establish or alter a cross-repository contract
must remain consistent with that governance record. A pull request should link
the relevant architectural decision and any coordinated documentation change.
If an architectural decision must change, update it through the governance
process in `cybersecgpt-docs` rather than treating an implementation change here
as the sole record.

This relationship is documentary and procedural; `cybersecgpt-foundation` has
no runtime or package dependency on `cybersecgpt-docs`.

## License

This project follows a source-available licensing model under the planned
CyberSecGPT Community Source License (CSL) Version 1.0. The final approved
license text will be supplied by the project owner before the first public
release. See [LICENSE](LICENSE) for the current licensing notice.
