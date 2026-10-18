# GenoLens

Local, private DNA reports inspired by consumer genetics sites—**GenoLens branded**, not a clone. Raw genomes stay on disk. Nothing is uploaded.

**Primary UI:** Next.js report app (`web/`) + FastAPI (`api/`).  
**Legacy UI:** Streamlit (`streamlit run genolens/app.py`).

**Documentation:** see the full set under [`docs/`](docs/README.md) (architecture, API, report hubs A–J, relatives/pedigree, reference data, development, troubleshooting).

**Version:** [`v0.0.1`](https://github.com/saeid-h/GenoLens/releases/tag/v0.0.1) — community standards + patch after baseline [`v0.0.0`](https://github.com/saeid-h/GenoLens/releases/tag/v0.0.0). See [`AGENTS.md`](AGENTS.md) for branching and releases.

**License:** [MIT](LICENSE) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

## Limits

- Exploratory only — not medical advice or clinical diagnosis.
- Ancient matches are population affinity, not proof of descent from named royals.
- Pedigree direction needs IBD2 and/or birth years; shared cM alone is symmetric.

## Agent rules

See [AGENTS.md](AGENTS.md).

## Setup

```bash
cd /path/to/GenoLens
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd web && npm install && cd ..
```

Place genotype files in `data/` (gitignored). Supported via `snps`: 23andMe, AncestryDNA, FTDNA, MyHeritage, VCF, and more.

## Run (professional UI)

Terminal 1 — API (localhost only):

```bash
source .venv/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 — web:

```bash
cd web
npm run dev
```

Open http://localhost:3000

### Reports (A→J)

Ancestry → Haplogroups → Traits → Wellness → Pharmacogenetics → Health → Relatives (primary + candidates) → Ancient → Archaic → Polygenic scores.

Relatives never auto-builds an N×N matrix over every file. Set optional birth years under **Settings → Samples & ages**.

## Legacy Streamlit

```bash
streamlit run genolens/app.py
```

## Open reference data

| Need | Source |
|------|--------|
| Ancient | [AADR](https://doi.org/10.7910/DVN/FFIDCW) / [Poseidon archive](https://server.poseidon-adna.org/explorer/aadr-archive) → `data/reference/` |
| PRS | [PGS Catalog](https://www.pgscatalog.org/) → optional `data/reference/prs/catalog.json` (demo weights ship in-package) |

Helpers: `genolens.reference`, `genolens.reference_catalog`.

## Tests

```bash
pytest -q
```

## Remote

GitHub: https://github.com/saeid-h/GenoLens.git — push only when asked; never commit `data/*.txt` or `my-docs/`.

## Stack

- `genolens` — ingest (`snps`), relatedness (`lineage`), AIM ancestry, panels, ancient, archaic, PRS
- `api` — FastAPI
- `web` — Next.js App Router (Fraunces + Source Sans 3, teal/coral brand)
- `docs/` — architecture, API, reports, ops (index: [docs/README.md](docs/README.md))
