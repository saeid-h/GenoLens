# Architecture

## High-level

```text
┌─────────────────────┐     REST JSON      ┌─────────────────────┐
│  web/ (Next.js)     │ ───────────────►   │  api/ (FastAPI)     │
│  Report hubs A–J    │   localhost only   │  Typed endpoints    │
└─────────────────────┘                    └──────────┬──────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │  genolens/ package  │
                                           │  ingest, ancestry,  │
                                           │  haplogroups, …     │
                                           └──────────┬──────────┘
                                ┌─────────────────────┼─────────────────────┐
                                ▼                     ▼                     ▼
                         data/*.txt            genolens/data/*.json   data/reference/
                         (gitignored)          (shipped panels)       (download-once)
```

Design rule: **SNP math stays in Python**. The TypeScript app is presentation and
orchestration only.

## Packages

| Path | Role |
|------|------|
| `genolens/` | Core analysis library |
| `genolens/data/` | Shipped JSON panels (AIM, haplogroups, health, archaic, PRS demo, named remains) |
| `api/` | Thin FastAPI wrapper; CORS limited to local Next origins |
| `web/` | Next.js App Router UI (Fraunces + Source Sans 3, teal/coral brand) |
| `tests/` | pytest coverage for core + API smoke |
| `docs/` | This documentation set |
| `data/` | Private genomes + optional reference downloads (**gitignored**) |

## Core modules (`genolens/`)

| Module | Responsibility |
|--------|----------------|
| `ingest.py` | Load any `snps`-supported file → `GenomeSummary` |
| `paths.py` | Sample listing, IDs/labels, default primary |
| `sample_meta.py` | Birth year / generation in `data/sample_meta.json` |
| `ancestry.py` | Softmax AIM continental affinity % |
| `haplogroups.py` | Shallow Y/mt tree walk (soft-pass missing parents) |
| `health.py` | Panel matching filtered by category hubs |
| `relatedness.py` | Pairwise IBD via `lineage`; pedigree inference |
| `ancient.py` | AADR / demo panel ranking + PCA helpers |
| `reference.py` | Download/prepare reduced AADR panel |
| `reference_catalog.py` | AADR/PGS status hints (no genome upload) |
| `archaic.py` | Neanderthal-informative SNP affinity |
| `prs.py` | Exploratory polygenic scores from local weights |
| `app.py` | **Legacy** Streamlit UI |

## Web routing

| Route | Purpose |
|-------|---------|
| `/` | Brand hero + CTA into reports |
| `/reports` | Hub cover cards A–J |
| `/reports/<slug>` | Detail page per hub |
| `/settings/samples` | Primary selection + birth year / generation |

Report slugs: `ancestry`, `haplogroups`, `traits`, `wellness`,
`pharmacogenetics`, `health`, `relatives`, `ancient`, `archaic`, `prs`.

## API boundary

- Bind: `127.0.0.1` (do not expose on `0.0.0.0` for private genomes).
- Next rewrites `/api/:path*` → `http://127.0.0.1:8000/api/:path*`.
- Genomes are never sent to the browser as raw files; only analysis JSON.

## Caching behavior

- FastAPI caches loaded genomes in-process (`lru_cache` on path string).
- Restart the API process after replacing a genotype file with the same path.
- Pairwise relatedness is computed on demand for selected pairs only.

## Constraints that shape the design

1. **No third-party genome upload** on the default path.
2. **No N×N compare** over every file in `data/` — primary × selected candidates.
3. **Directed pedigree** requires IBD2 and/or ages; shared cM alone is symmetric.
4. **Open data only** for reference enrichment (AADR, PGS Catalog, ClinVar-style panels).

See also [Privacy and limits](privacy-and-limits.md) and [Relatives and pedigree](relatives-and-pedigree.md).
