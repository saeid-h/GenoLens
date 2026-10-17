# Privacy and limits

## Privacy model

GenoLens is built for **local analysis**:

- Genotype files live under `data/` on your machine.
- The FastAPI server should bind to **localhost only**.
- The Next.js UI talks to that local API (proxy or `NEXT_PUBLIC_API_BASE`).
- Analysis does **not** upload raw genomes to third-party consumer DNA APIs.

What may leave the machine (only when you explicitly download/reference tools):

- Fetching **open reference datasets** (AADR package, optional PGS Catalog metadata)
  into `data/reference/`.
- Optional annotation lookups (PGS Catalog REST for score metadata) — these do
  **not** send your genotypes.

## Never commit

| Path | Why |
|------|-----|
| `data/*.txt` (and other genotype globs) | Private genomes |
| `data/sample_meta.json` | Personal ages / labels |
| `data/reference/` | Large / redistributable dumps |
| `my-docs/` | Personal agent knowledge base |
| `.env` | Local secrets |

These patterns are listed in `.gitignore`. Agents and humans must not stage them.

## Product disclaimers (always)

Every report hub should be read with these limits:

1. **Not medical advice.** Trait, wellness, pharmacogenetics, carrier, and PRS
   results are exploratory literature-style notes, not diagnoses or dosing guidance.
2. **Not clinical carrier testing.** Heterozygous calls on a microarray are not
   a clinical report.
3. **Not proof of royal / named ancient descent.** Ancient affinity ranks
   individuals and groups by genotype overlap / PCA neighborhood — affinity, not
   genealogy to a named person.
4. **Haplogroups are shallow.** Consumer chips miss many defining SNPs; GenoLens
   reports deepest matched branch plus markers called/tested.
5. **Pedigree direction needs more than cM.** Parent–child and full siblings can
   share similar total cM; use IBD2 and/or birth years.

Canonical disclaimer string (API):

> Exploratory only. Not medical advice, not a clinical diagnosis, and not proof of
> descent from any named historical person.

## Paid / upload APIs — out of scope for v1

Do **not** add as default dependencies:

- Genomelink, Promethease, Gencove DTC upload APIs, white-label admixture upload services

Optional free annotation sources (metadata only) are fine: NCBI, Ensembl, PGS Catalog.

## Network exposure

If you run the stack on a shared machine:

- Prefer `127.0.0.1`, not `0.0.0.0`.
- Do not put GenoLens behind a public reverse proxy without authentication and a
  clear threat model — genomes would then be reachable to anyone who can hit the API.

## Related docs

- [Data and formats](data-and-formats.md)
- [Open reference data](reference-data.md)
- [Report hubs](reports.md)
