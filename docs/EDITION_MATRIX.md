# CyberSecGPT Foundation Edition Matrix

## Status

This matrix applies to the `0.1.x` alpha line of `cybersecgpt-foundation`. It
classifies this repository's existing capabilities; it does not announce the
availability or release status of a complete CyberSecGPT product edition.

Supported states are `Included`, `Limited`, `Add-on`, `Preview`, `Deprecated`,
and `Not available`.

## Availability

| Foundation capability | Community | Professional | Enterprise |
| --- | --- | --- | --- |
| Package version metadata | Included | Included | Included |
| Shared project constants | Included | Included | Included |
| Foundation exception hierarchy | Included | Included | Included |
| Immutable typed identifiers | Included | Included | Included |
| Security context contract | Included | Included | Included |
| Audit event contracts | Included | Included | Included |
| Structural validation helpers | Included | Included | Included |
| Deterministic JSON helpers | Included | Included | Included |
| Opt-in standard logging helpers | Included | Included | Included |
| JSON-compatible typing aliases | Included | Included | Included |
| Timezone-aware UTC helpers | Included | Included | Included |

Professional and Enterprise receive these capabilities through the same shared
foundation package. The implementations are not duplicated by edition.

## Repository boundary

The following capabilities are intentionally absent from this repository:

- product-edition selection
- entitlement acquisition or validation
- license-document parsing
- feature gating
- organization roles or authorization
- subscription, seat, usage, or deployment limits
- premium workflows and proprietary business logic

Those concerns require approved architecture and product placement before
implementation. When introduced elsewhere, licensing decisions must remain
separate from authorization, and lower editions must not depend on
higher-edition packages.

## Upgrade, downgrade, and data behavior

The current foundation primitives are stateless and store no project or
edition-specific data. They therefore require no edition migration and do not
delete, hide, or transform user data during an upgrade or downgrade.

Any future stateful or edition-aware capability must document:

- preserved data and configuration
- behavior when an entitlement changes
- read and export availability after downgrade
- compatibility and migration requirements
- security and privacy impact

## Change control

Every new capability must be classified before implementation. The decision
record must identify the user problem, target edition, security impact,
operational impact, dependencies, deployment model, maintenance and support
burden, compatibility, licensing implications, and data handling.

Significant placement decisions require approval from authorized product
leadership and a corresponding product or architecture decision record. This
matrix must be updated in the same reviewed change.
