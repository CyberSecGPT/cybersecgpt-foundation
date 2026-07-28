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
- `bugfix`
- `hotfix`
- `docs`
- `refactor`
- `test`
- `chore`
- `security`

Examples:

```text
feature/foundation-bootstrap
bugfix/version-export-consistency
docs/clarify-package-boundaries
```

The `main`, `release/*`, and `hotfix/*` branches are protected. Direct commits
to protected branches are prohibited; changes must pass review and repository
quality gates before integration.

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
python -m mypy src scripts
```

Use complete type annotations for new public interfaces. Keep the code
compatible with strict mypy checking, and keep any suppression narrowly scoped
and justified.

Validate documentation and repository security boundaries:

```bash
python scripts/validate_repository.py
python -m pip check
```

To apply the project formatter:

```bash
python -m black .
```

Build and verify the distribution boundary:

```bash
python -m build
python scripts/verify_distribution.py dist
```

## Edition and feature placement

This repository is shared Community-layer infrastructure. Higher editions may
depend on its public contracts; this package must not depend on Professional or
Enterprise code.

Before implementing an edition-aware capability:

1. Record the user problem, target edition, security and data impact,
   dependencies, compatibility requirements, and licensing implications.
2. Obtain product-governance approval for the feature placement.
3. Update [docs/EDITION_MATRIX.md](docs/EDITION_MATRIX.md).
4. Keep authorization separate from commercial entitlement decisions.
5. Use an approved centralized capability interface rather than scattered
   edition-name conditionals.

Do not place premium business logic, commercial credentials, private signing
keys, or proprietary assets in this repository.

## Architecture governance

Review the repository architecture in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before changing module boundaries
or dependency direction.

The authoritative cross-repository architecture and architectural decisions
are maintained in
[`cybersecgpt-docs`](https://github.com/CyberSecGPT/cybersecgpt-docs).

Before changing a shared contract, public package boundary, dependency
direction, or platform-wide convention:

1. Review the relevant architectural material in `cybersecgpt-docs`.
2. Create or update an Architecture Decision Record for a significant
   technical decision.
3. Confirm that the implementation is consistent with the recorded decision.
4. Link the relevant decision from the pull request.
5. Coordinate an architecture documentation update when the decision or
   contract changes.

An Architecture Decision Record must state its title, context, problem,
considered options, decision, rationale, consequences, and rejected
alternatives. Resolve technical disagreements through evidence, prototypes,
benchmarks, security analysis, and architectural review.

This package must remain dependency-light and must not depend on another
CyberSecGPT repository.

## Dependency governance

The bootstrap has no runtime dependencies. A proposed dependency requires
maintainer review of its necessity, maintenance activity, maturity, security
history, license compatibility, community support, supply-chain risk, and
long-term sustainability. Prefer the Python standard library whenever
practical.

An approved dependency change must update package metadata, architecture
documentation, tests, the changelog, and distribution-boundary verification
where applicable.

## Pull request expectations

Pull requests should:

- Be focused on one coherent change.
- Include a summary, motivation, implementation details, and user-visible
  effect.
- Link a related issue or architectural decision when one exists.
- Include or update tests and documentation as needed.
- Provide testing evidence and the exact validation commands that passed.
- Describe compatibility, migration, or security implications.
- Pass all continuous integration checks.
- Avoid unrelated formatting or generated-file changes.
- Address review feedback with additional commits or a clear technical
  explanation.

Every pull request requires review before merge. Contributors and AI coding
agents must not approve their own changes.

Reviewers evaluate correctness, readability, maintainability, security,
testing, documentation, performance, and architectural consistency.

Report undisclosed vulnerabilities through the private process in
[SECURITY.md](SECURITY.md), not through a public pull request or issue.

## Contributor License Agreement and licensing

External contributors must accept the CyberSecGPT Contributor License Agreement
before their contributions can be merged. Repository maintainers coordinate
the approved CLA process and verify acceptance during review.

Contributions to this repository are intended for distribution under the
CyberSecGPT Community Source License (CSL) Version 1.0. The final approved
license text will be supplied by the project owner before the first public
release.

## Release and exception governance

Only repository maintainers may approve a release. A release requires all
quality gates, consistent versions, current documentation and changelog,
release notes, and an edition-matrix review. This Bootstrap repository has no
approved public release.

An exception to repository governance requires documented approval, including
its justification, scope, duration, mitigation, and review date.
Permanent exceptions require Founder approval. Exceptions must not weaken
applicable security requirements or approved legal agreements.

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
