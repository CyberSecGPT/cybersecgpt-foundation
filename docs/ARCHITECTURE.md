# cybersecgpt-foundation Architecture

## Status and governance

`cybersecgpt-foundation` is in the Bootstrap lifecycle stage and remains alpha
software. This document describes the repository-level architecture.
Cross-repository decisions, platform dependency direction, and significant
architectural changes are governed through `cybersecgpt-docs`.

Changes that alter a public contract, layer boundary, or dependency direction
require architectural review and an Architecture Decision Record through the
governed documentation process.

## Role in the platform

The repository occupies the Foundation layer of the CyberSecGPT architecture:

```text
Applications
    ↓
Feature modules
    ↓
Shared libraries
    ↓
Foundation
    ↓
Platform
```

Higher layers may consume the foundation package. This package must not depend
on feature modules, applications, or another CyberSecGPT repository.

## Edition boundary

This repository belongs to the shared Community layer. Professional and
Enterprise implementations may extend its public contracts without copying or
modifying the Community package:

```text
Enterprise extensions
    ↓ depends on
Professional extensions
    ↓ depends on
Community and shared foundation
```

Dependency flow in the opposite direction is prohibited. The foundation wheel
contains no premium implementation, entitlement enforcement, commercial
credentials, or proprietary assets.

Edition placement is recorded in
[EDITION_MATRIX.md](EDITION_MATRIX.md). No edition-aware runtime feature exists
in this bootstrap, so a feature registry or licensing service is not introduced
prematurely. A future edition-aware capability requires approved placement and
must use centralized capability interfaces that keep entitlement separate from
authorization.

## Scope

The package owns small, stable, cross-cutting Python primitives:

- project constants and version metadata
- a common exception hierarchy
- immutable identifiers
- immutable security-context contracts for opaque actor and trace identity
- immutable audit-event contracts for structured security-relevant records
- reusable validation helpers
- deterministic JSON conversion
- opt-in logging configuration
- JSON-compatible typing aliases
- timezone-aware UTC helpers

Application behavior, cybersecurity product logic, model workflows,
persistence, network services, user interfaces, deployment, and infrastructure
remain outside this repository.

## Source layout

Production code uses a `src` layout:

```text
src/cybersecgpt/
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
```

Tests mirror the public behavior under `tests/`. Repository documentation lives
under `docs/`, and automation lives under `scripts/` and `.github/`.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `constants` | Stable project and serialization defaults |
| `exceptions` | Domain-specific foundation error hierarchy |
| `identifiers` | Immutable string identifiers and UUID4 generation |
| `validation` | Shared structural string and integer validation |
| `serialization` | Deterministic JSON encoding and decoding |
| `security.context` | Immutable opaque actor and trace context |
| `security.audit` | Immutable structured audit-event contracts |
| `logging` | Explicit root configuration and validated logger lookup |
| `typing` | Recursive JSON-compatible type aliases |
| `utils` | Timezone-aware UTC values and ISO 8601 text |
| `version` | Canonical package version |

Each module has one primary responsibility and an explicit `__all__`. The
top-level `cybersecgpt` package exports only `__version__`; the
`cybersecgpt.foundation` package exposes the conservative runtime API.

## Internal dependency direction

Leaf modules depend only on the Python standard library. Internal dependencies
flow toward shared validation and errors:

```text
identifiers ──────→ exceptions
validation ──────→ exceptions
serialization ────→ constants, exceptions, validation
security.context ─→ identifiers, validation
security.audit ───→ identifiers, serialization, typing, utils, validation, security.context
logging ─────────→ validation
```

The package initializers re-export public objects but contain no application
logic. Imports do not configure logging or perform external I/O.

## Behavioral boundaries

Identifiers validate only structural string constraints. Manually supplied
values are not required to use UUID syntax; UUID4 is used only by `new()`.

Validation helpers return accepted values unchanged and raise
`ValidationError` with field-specific messages.

JSON serialization sorts mapping keys, preserves Unicode, and converts
standard-library codec failures into `SerializationError` while retaining the
original cause.

Logging configuration is opt-in. It configures the root logger only when no
handlers exist, preserving application ownership of logging destinations.

`SecurityContext` carries structural actor and trace identity only. It does
not contain authentication state, credentials, roles, permissions,
entitlements, or authorization decisions.

`AuditEvent` records a security-relevant outcome supplied by a higher layer.
The `DENIED` value is a recorded outcome only; Foundation does not decide
whether an operation is authorized. Audit metadata is defensively immutable
and canonicalized through the shared deterministic JSON serializer. Metadata
is not automatically redacted, so callers remain responsible for excluding
credentials, secrets, tokens, and inappropriate sensitive data.

## Dependencies and portability

Runtime code uses only the Python standard library and supports Python 3.11,
3.12, and 3.13. Development tools are isolated in the `dev` optional
dependency group. The package has no runtime dependency on another
CyberSecGPT repository.

Repository text is normalized through `.gitattributes` for consistent
cross-platform behavior.

## Quality gates

Changes must pass:

- Ruff linting
- Black formatting checks
- strict mypy analysis
- deterministic unit tests
- 100% statement and branch coverage
- repository documentation and local-link validation
- credential, private-key material, and access-token pattern scanning
- installed dependency consistency checks
- source and wheel builds
- distribution content, dependency, edition-boundary, and license-metadata
  verification
- repository whitespace validation

Protected branches require review. Releases and public API changes require
maintainer approval and coordinated documentation updates.
