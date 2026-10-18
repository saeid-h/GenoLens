# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| Latest release on GitHub (and current `main`) | Yes |
| Older tags | Best effort only |

Package / API version strings track the latest release tag (see `README.md` and
`pyproject.toml`).

## Reporting a vulnerability

Please report security issues **privately** via
[GitHub Security Advisories](https://github.com/saeid-h/GenoLens/security/advisories/new)
for this repository. Do not open a public issue for unfixed vulnerabilities.

Include enough detail to reproduce the problem (steps, affected routes or
components, and impact). We will acknowledge reports and work toward a fix.

## Scope

**In scope:** vulnerabilities in GenoLens application code (`genolens/`, `api/`,
`web/`) on the intended local stack (localhost API and UI).

**Out of scope:**

- Medical, clinical, or diagnostic claims — GenoLens is exploratory only.
- User genotype files and private sample metadata — **never** attach or upload
  genomes when reporting issues. See
  [`docs/privacy-and-limits.md`](docs/privacy-and-limits.md).
- Issues that require committing or sharing files under `data/`,
  `data/reference/`, or `my-docs/`.

## Privacy reminder

GenoLens is designed so raw genomes stay on the operator’s disk. Do not propose
or ship a default path that uploads genomes to third parties.
