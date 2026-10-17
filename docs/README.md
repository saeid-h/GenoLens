# GenoLens documentation

GenoLens is a **local**, privacy-first DNA report app. Raw genotype files stay
on disk under `data/`. Analysis runs through the Python package `genolens`,
served by a localhost FastAPI layer (`api/`) and a Next.js report UI (`web/`).

Reports are **exploratory** — not medical advice, clinical diagnosis, or proof
of descent from any named historical person.

## Start here

| Doc | Contents |
|-----|----------|
| [Getting started](getting-started.md) | Install, add samples, run API + web |
| [Architecture](architecture.md) | Packages, data flow, design constraints |
| [Privacy and limits](privacy-and-limits.md) | What stays local, disclaimers, non-goals |
| [Data and formats](data-and-formats.md) | Supported files, IDs, metadata, gitignore |
| [API reference](api.md) | REST endpoints, request/response shapes |
| [Report hubs A–J](reports.md) | What each report shows and how it is computed |
| [Relatives and pedigree](relatives-and-pedigree.md) | Primary×candidates, IBD2, directed trees |
| [Open reference data](reference-data.md) | AADR, PGS Catalog, panels, download-once |
| [Development](development.md) | Tests, layout, agent rules, contribution notes |
| [Troubleshooting](troubleshooting.md) | Common failures and fixes |
| [Legacy Streamlit](legacy-streamlit.md) | Older UI still available for spot checks |

## Quick links

- Root runbook: [`README.md`](../README.md)
- Agent rules: [`AGENTS.md`](../AGENTS.md)
- Remote: https://github.com/saeid-h/GenoLens.git

## Default ports

| Service | URL |
|---------|-----|
| Next.js UI | http://localhost:3000 |
| FastAPI | http://127.0.0.1:8000 |
| OpenAPI docs | http://127.0.0.1:8000/docs |

The web app proxies `/api/*` to the FastAPI process (see `web/next.config.mjs`).
