# cybersecgpt-foundation

**Project status: Alpha (0.1.0).** The package is under active development.
Public APIs may change before a stable release.

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
- String and integer validation helpers.
- Deterministic JSON serialization and deserialization.
- Idempotent, opt-in logging configuration and validated logger lookup.
- Timezone-aware UTC datetime and ISO 8601 helpers.
- Stable project constants and recursive JSON-compatible typing aliases.

These primitives use only the Python standard library and remain intentionally
independent of application frameworks and other CyberSecGPT repositories.

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
python -m mypy src
```

Build the distribution artifacts:

```bash
python -m build
```

## Package structure

```text
src/
└── cybersecgpt/
    ├── __init__.py
    └── foundation/
        ├── __init__.py
        ├── constants.py
        ├── exceptions.py
        ├── identifiers.py
        ├── logging.py
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
├── test_serialization.py
├── test_typing.py
├── test_utils.py
├── test_validation.py
└── test_version.py
```

The top-level `cybersecgpt` package and the `cybersecgpt.foundation` package
both expose the package version.

## Architecture governance

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

This project is licensed under the MIT License. See [LICENSE](LICENSE).
