# Open reference data

GenoLens prefers **download once, analyze offline**. Reference blobs live under
`data/reference/` (gitignored). Shipped JSON under `genolens/data/` covers the
default path without network.

## Status endpoint

```bash
curl -s http://127.0.0.1:8000/api/reference/status
```

Returns AADR download hints, ancient panel status, and PRS catalog locality.

Helpers:

- `genolens.reference` — AADR download / extract / reduce to panel
- `genolens.reference_catalog` — PGS REST metadata + directory layout

---

## Ancient DNA (AADR)

| Item | Detail |
|------|--------|
| Primary sources | [AADR Dataverse](https://doi.org/10.7910/DVN/FFIDCW), [Poseidon AADR archive](https://server.poseidon-adna.org/explorer/aadr-archive) |
| Local target | `data/reference/` (zip + extracted package + reduced `panel/`) |
| Runtime | `ancient.rank_matches`, `project_pca`, `ancient_status` |

### Behavior without a full download

If a prepared panel is missing, the API may build a **demo panel** so the Ancient
hub still renders. Demo results are for UI plumbing — not research-grade affinity.

### Preparing a real panel (outline)

1. Ensure enough disk and a stable network.
2. Use `genolens.reference.download_aadr` / `extract_aadr` / prepare helpers
   (see module docstrings) to produce `data/reference/panel/genotypes.npz` and
   `annotation.csv`.
3. Restart the API and reopen `/reports/ancient`.

Full AADR packages are large; do not commit them.

---

## Polygenic scores (PGS Catalog)

| Item | Detail |
|------|--------|
| Catalog | https://www.pgscatalog.org/ |
| Shipped default | `genolens/data/prs_demo.json` |
| Optional override | `data/reference/prs/catalog.json` |
| Download helper | `scripts/download_pgs_catalog.py` |
| Metadata fetch | `fetch_pgs_score_metadata(pgs_id)` (annotation only) |

### Do you need a download?

No for understanding the hub (demo mode is enough). Yes if you want published
open weights instead of synthetic demos.

**Not practical:** downloading the *entire* PGS Catalog (~7k scores, many with
10k–1M+ variants). Giant panels barely overlap a 23andMe chip and would make
scoring/UI unusable.

**Default download (best judgment):** a **diverse** subset — about **80** scores,
preferring different traits, each with **≤100 variants**, converted to local JSON:

```bash
.venv/bin/python scripts/download_pgs_catalog.py
# optional: --max-variants 200 --limit 150
```

Writes gitignored `data/reference/prs/catalog.json`. Restart the API afterward;
`/reports/prs` should leave demo mode (filter/sort by chip coverage).

Expected conceptual shape (simplified):

```json
{
  "mode": "catalog",
  "disclaimer": "Exploratory only…",
  "scores": [
    {
      "id": "PGS000001",
      "trait": "Breast cancer",
      "variants": [
        { "rsid": "rs123", "effect_allele": "A", "weight": 0.01 }
      ]
    }
  ]
}
```

Scores report raw weighted dosage sums and markers used/missing — not calibrated
clinical risk. Cite PGS Catalog / the original publications; follow EBI terms.

---

## Archaic panel

Shipped: `genolens/data/archaic_panel.json` — small published-style informative
SNP list for Neanderthal allele sharing counts.

---

## Health / trait panels

Shipped: `genolens/data/health_panel.json`.

Markers include `category` for hub filtering (`trait`, `metabolism`, `wellness`,
`pharmacogenetics`, `health`, `carrier`). Prefer redistributable ClinVar /
literature rsID lists — do not scrape proprietary pages into the repo.

---

## Haplogroup trees

Shipped: `genolens/data/haplogroups.json` (Y + mt). MT entries may use `chrom` +
`pos` when rsIDs are missing on consumer chips. Expand carefully against local
chip rsID/position coverage.

---

## AIM ancestry

Shipped: `genolens/data/aim_panel.json` — denser AISNP-style markers with
**1000 Genomes Phase 3 population** allele frequencies (Ensembl), plus region
rollups. Rebuild offline-ready panel (needs network once):

```bash
python scripts/build_ancestry_panel.py
```

Optional `ezancestry` extra is not required.

---

## Citation practice

When documenting results externally, cite:

- AADR / Allen Ancient DNA Resource (Reich lab / collaborators)
- PGS Catalog for any catalog-derived weights
- Original papers for specific pharmacogenetic or archaic SNPs

GenoLens report footnotes should stay honest about demo vs prepared panels.

## Related docs

- [Report hubs](reports.md)
- [Privacy and limits](privacy-and-limits.md)
- [Getting started](getting-started.md)
