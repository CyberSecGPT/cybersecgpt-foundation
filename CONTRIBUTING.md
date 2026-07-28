# Contributing to cybersecgpt-foundation

Thank you for contributing to the shared foundation of the CyberSecGPT
platform.

## Branch naming

Create branches from the current default branch and use a concise, lowercase,
hyphenated name:

```text
<type>/<short-kebab-case-summary>
```

Common types include:

- `feature`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `security`

Examples:

```text
feature/foundation-bootstrap
fix/version-export-consistency
docs/clarify-package-boundaries
```

## Development setup

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

Install the package and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Test requirements

Every behavior change must include appropriate tests. Bug fixes should include
a regression test that fails without the fix.

Tests must be deterministic, isolated, and independent of network access or
other CyberSecGPT repositories. Run the complete suite before opening or
updating a pull request:

```bash
python -m pytest --cov=cybersecgpt --cov-report=term-missing --cov-fail-under=100
```

Do not weaken existing assertions or coverage configuration merely to make a
change pass.

## Linting, formatting, and type checking

All contributions must pass:

```bash
python -m ruff check .
python -m black --check .
python -m mypy src
```

Use complete type annotations for new public interfaces. Keep the code
compatible with strict mypy checking, and keep any suppression narrowly scoped
and justified.

To apply the project formatter:

```bash
python -m black .
```

## Architecture governance

The authoritative cross-repository architecture and architectural decisions
are maintained in
[`cybersecgpt-docs`](https://github.com/CyberSecGPT/cybersecgpt-docs).

Before changing a shared contract, public package boundary, dependency
direction, or platform-wide convention:

1. Review the relevant architectural material in `cybersecgpt-docs`.
2. Confirm that the implementation is consistent with the recorded decision.
3. Link the relevant decision from the pull request.
4. Coordinate an architecture documentation update when the decision or
   contract changes.

This package must remain dependency-light and must not depend on another
CyberSecGPT repository.

## Pull request expectations

Pull requests should:

- Be focused on one coherent change.
- Explain the motivation, scope, and user-visible effect.
- Link a related issue or architectural decision when one exists.
- Include or update tests and documentation as needed.
- Describe compatibility, migration, or security implications.
- Report the validation commands that were run.
- Pass all continuous integration checks.
- Avoid unrelated formatting or generated-file changes.
- Address review feedback with additional commits or a clear technical
  explanation.

Report undisclosed vulnerabilities through the private process in
[SECURITY.md](SECURITY.md), not through a public pull request or issue.

## Conventional commits

Use a Conventional Commit-style subject written in the imperative mood.
Examples:

```text
feat: expose package version metadata
fix: keep foundation version exports consistent
docs: define foundation architecture boundary
test: cover public version exports
chore: configure strict type checking
```
