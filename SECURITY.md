# Security Policy

## Reporting a vulnerability

Do not report an undisclosed vulnerability in a public issue, discussion, pull
request, or commit message.

Submit reports privately through GitHub's
[private vulnerability reporting form](https://github.com/CyberSecGPT/cybersecgpt-foundation/security/advisories/new).
Reports submitted there are visible only to authorized repository maintainers.

If the private form is unavailable, contact a repository maintainer through an
established private channel. If no private channel is available, open a public
issue containing only a request to establish private contact. Do not include
the affected component, technical details, evidence, or any information that
could help reproduce the vulnerability.

## Information to include

Provide enough information for the maintainers to reproduce and assess the
issue:

- The affected package version or commit.
- The relevant Python version, operating system, and configuration.
- The vulnerability type and affected component.
- A clear description of the impact and realistic attack scenario.
- Reproduction steps or a minimal proof of concept.
- Required privileges, preconditions, or user interaction.
- Sanitized logs, traces, or screenshots when useful.
- Known mitigations or remediation suggestions.
- Any planned disclosure date or coordination requirements.

Do not include credentials, access tokens, personal data, or data obtained from
systems you were not authorized to test.

## Supported versions

The repository is in its Bootstrap lifecycle stage and has no public release.
Security reports against the current repository state are accepted and
prioritized, but no released version is currently supported.

| Version or state | Support status |
| --- | --- |
| Current repository state | Pre-release security review |
| Public releases | None published |

This table will be updated before the first public release. After releases
begin, security updates may require upgrading to the newest supported version.

## Responsible disclosure

Researchers are expected to:

- Act in good faith and test only systems they are authorized to assess.
- Limit testing to what is necessary to confirm the vulnerability.
- Avoid privacy violations, data destruction, persistence, service disruption,
  and social engineering.
- Keep vulnerability details confidential while remediation and disclosure are
  coordinated.
- Allow the maintainers a reasonable opportunity to investigate and release a
  fix.
- Coordinate public disclosure through the private report.

Maintainers will assess the report, request additional information when
necessary, and coordinate remediation and disclosure through the private
channel. Disclosure timing depends on severity, complexity, and release
readiness. Reporter credit will be handled according to the reporter's
preference when recognition is appropriate.

Public issues must never contain details of an undisclosed vulnerability.
