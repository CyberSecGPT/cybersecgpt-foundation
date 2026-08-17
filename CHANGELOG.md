# Changelog

This file records notable changes to `cybersecgpt-foundation`. Releases require
maintainer approval and must satisfy the repository quality gates.

## Unreleased

### Added

- Initial Python package bootstrap and version metadata.
- Shared constants, exception hierarchy, typed identifiers, validation
  helpers, deterministic JSON serialization, logging helpers, JSON typing
  aliases, and UTC time utilities.
- Immutable `SecurityContext` contract for opaque actor and trace identity.
- Immutable audit-event contracts with typed identity, UTC timestamps,
  severity and outcome enums, immutable JSON metadata, and deterministic
  serialization/deserialization.
- Immutable `EvidenceRef` contract for opaque evidence location, digest,
  algorithm, source, and optional media-type metadata.
- Public defensive JSON safety-bound constants for payload size, nesting,
  container size, node count, string values, and object keys.
- Unit tests with full statement and branch coverage.
- Continuous integration across Python 3.11, 3.12, and 3.13.
- Repository governance, security, contribution, and architecture
  documentation.
- Version-controlled edition positioning and distribution-boundary
  verification.
- Automated documentation, local-link, sensitive-material, and dependency
  consistency checks.

### Changed

- Updated repository licensing metadata for the planned CyberSecGPT Community
  Source License (CSL) Version 1.0.
- Export JSON-compatible typing aliases from the public `cybersecgpt.foundation`
  API to match documented edition availability.
- JSON serialization and deserialization now enforce package-wide defensive
  payload and structural safety ceilings.
- Bound development and build dependency versions for more stable CI
  resolution.
- Accept PEP-compliant Core Metadata versions 2.4 and newer within major
  version 2 during distribution verification.

### Fixed

- Distribution verification no longer rejects valid `Metadata-Version: 2.5`
  wheel and source-archive metadata emitted by current Hatchling releases.
