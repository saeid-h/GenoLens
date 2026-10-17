# Data and formats

## Directory layout

```text
data/                          # gitignored content (except placeholders)
  genome_*.txt                 # private genotypes
  *.csv / *.tsv / *.vcf …      # other supported raw files
  sample_meta.json             # birth year / generation (optional)
  reference/
    panel/                     # prepared reduced AADR-style panel
    aadr/                      # raw AADR download (optional)
    prs/catalog.json           # optional PGS weights override

genolens/data/                 # shipped with the package (tracked)
  aim_panel.json
  haplogroups.json
  health_panel.json
  archaic_panel.json
  prs_demo.json
  named_remains.json
```

## Sample IDs and labels

| Concept | Rule | Example |
|---------|------|---------|
| **id** | Filename stem | `genome_Saeid_Hosseinipoor_v5_Full_20220131131756` |
| **label** | Humanized stem (strips `genome_`, chip suffixes) | `Saeid Hosseinipoor` |

API routes accept **id** (preferred) or **label**. Resolution is in
`genolens.paths.resolve_sample`.

### Default primary

If a file stem contains
`genome_Saeid_Hosseinipoor_v5_Full_20220131131756`, that sample is preferred as
default primary; otherwise the first sorted file is used.

## Supported ingest formats

Ingest always goes through `snps.SNPs` (`genolens.ingest.load_genome`):

1. Parse file → genotype table (rsID / chrom / pos / genotype).
2. Prefer GRCh37 / consumer-chip coordinates as provided by `snps`.
3. Downstream modules only see the normalized table + genotype lookup.

Chip differences (v3/v4/v5, AncestryDNA, etc.) change **overlap**. Reports should
surface **markers used / missing**, not pretend every file has equal depth.

## Sample metadata (`sample_meta.json`)

Created/updated via **Settings → Samples & ages** or
`PUT /api/samples/{id}/meta`.

Example shape:

```json
{
  "samples": {
    "genome_Example_v5_Full_…": {
      "birth_year": 1950,
      "generation": "parent",
      "display_name": "Example"
    }
  }
}
```

Fields:

| Field | Use |
|-------|-----|
| `birth_year` | Orient parent → child when ≥ ~15 years apart |
| `generation` | Free-text label for the user |
| `display_name` | Optional override (UI may still show file-derived label) |

This file is **gitignored**. Do not commit ages.

## Shipped panels vs downloads

| Need | Default | Optional upgrade |
|------|---------|------------------|
| Ancestry % | Bundled AIM panel | Denser open AISNP / HO refs later |
| Haplogroups | Bundled Y/mt defining SNPs | Expand trees for new chips |
| Traits / wellness / pharma / carrier | Bundled `health_panel.json` | Curated ClinVar subsets |
| Ancient | Demo panel if AADR missing | Full AADR → `data/reference/panel/` |
| Archaic | Bundled small SNP list | Larger published archaic lists |
| PRS | Bundled `prs_demo.json` | `data/reference/prs/catalog.json` |

## Genome summary fields

`GET /api/samples/{id}/overview` returns (among others):

- `source` — vendor/parser source string from `snps`
- `build` / `assembly`
- `count` — number of SNPs loaded
- `sex` — SNP-derived sex when available
- `chip` — chip string when `snps` exposes one
- `meta` — from `sample_meta.json`

## Related docs

- [Getting started](getting-started.md)
- [Open reference data](reference-data.md)
- [Privacy and limits](privacy-and-limits.md)
