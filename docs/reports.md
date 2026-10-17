# Report hubs (A–J)

The professional UI ships ten hubs in fixed order. Each page shows a short
explainer, disclaimer, visualization or table, and marker/coverage notes where
available.

| Letter | Hub | Route | Backend |
|--------|-----|-------|---------|
| A | Ancestry Composition | `/reports/ancestry` | `ancestry.predict_ancestry` |
| B | Haplogroups | `/reports/haplogroups` | `haplogroups.call_haplogroups` |
| C | Traits | `/reports/traits` | health panel `trait` |
| D | Wellness | `/reports/wellness` | `metabolism` + `wellness` |
| E | Pharmacogenetics | `/reports/pharmacogenetics` | `pharmacogenetics` |
| F | Health & carrier | `/reports/health` | `health` + `carrier` |
| G | DNA Relatives | `/reports/relatives` | compare + pedigree |
| H | Ancient affinity | `/reports/ancient` | `ancient` + reference panel |
| I | Archaic affinity | `/reports/archaic` | `archaic.score_archaic` |
| J | Polygenic scores | `/reports/prs` | `prs.score_prs` |

---

## A — Ancestry Composition

**Intent:** Genotype likelihood affinity against **1000 Genomes Phase 3 analysis
populations** (26 groups), rolled up into continental regions. Built from a denser
open AIM panel (`genolens/data/aim_panel.json`; rebuild with
`scripts/build_ancestry_panel.py`).

**Not claimed:** Country ethnicity, tribal identity, or legal ancestry. 1000 Genomes
has **no** Iranian / Levant / North Africa panels — West Asian samples often look
closest to South Asian (GIH/ITU/PJL) and/or Southern European (TSI/IBS).

**UI:** Regional **pie + bars**, table of closest 1000 Genomes populations (linked
to `/catalog/ancestry/[code]`), markers used / total; temperature-scaled
likelihood to reduce fake 99% certainty. Catalog blurbs are first-party GenoLens
copy — reference populations, not scraped ethnicity pages.

**Upgrade path:** Human Origins / AADR modern references for MENA-aware labels.

---

## B — Haplogroups

**Intent:** Shallow paternal (Y) and maternal (mt) haplogroup **hints** from a
bundled defining-SNP tree (ISOGG-linked public rsIDs).

**Important fix:** If a parent marker is missing on the chip, the walker
**soft-passes** and still tests children. Position-based MT markers (chrom+pos)
are used when rsIDs are absent on v5-class chips. Y defining SNPs must use the
correct rsID/allele (e.g. CT = M168/`rs2032595`, not M45).

**UI:** Tip haplogroup, path (e.g. `BT → CT → CF → P`), markers called/tested,
evidence table, note comparing to 23andMe depth.

**Limits:** 23andMe scores thousands of Y SNPs including private i-ids, so their
paternal tip is usually much finer than GenoLens. GenoLens is an open shallow
tree — expect broader branches (CT/CF/P), not terminal 23andMe labels.

---

## C — Traits

**Intent:** Non-clinical trait markers (taste, pigmentation, earwax, muscle,
research associations) from the curated panel.

**UI:** **Prediction cards** first (topic illustration + headline like “Likely
brown eyes”), optional **phenotype sketch** (SVG face from a few SNPs — playful,
not a photo), then full marker table. Panel markers may carry `topic` /
`predictions` fields; API hits include resolved `prediction`.

---

## D — Wellness

**Intent:** Metabolism / alcohol / folate / sleep-adjacent markers
(`metabolism`, `wellness` categories).

**UI:** Prediction cards + full table. Exploratory only — not nutrition or sleep advice.

---

## E — Pharmacogenetics

**Intent:** CYP / TPMT / SLCO1B1-style drug-gene markers with **strong caveats**.

**Never:** Recommend starting/stopping medication from GenoLens alone.

**UI:** Prediction cards + full table; disclaimer under “About this result.”

---

## F — Health & carrier

**Intent:** Small redistributable carrier/health-style subset with non-diagnostic
wording (“not a diagnosis”, “seek clinical testing”).

**Categories:** `health`, `carrier` only (traits/pharma/wellness are separate hubs).

**UI:** Prediction cards + full table.

---

## G — DNA Relatives

See the dedicated guide: [Relatives and pedigree](relatives-and-pedigree.md).

Summary:

- Choose **primary** (settings) and **candidates** (chips on relatives page).
- Compare selected pairs; when 3–8 people are selected, **candidate × candidate**
  pairs (e.g. mother × grandmother) are included via family-tree triangulation.
- UI groups **With you** vs **Among selected relatives**.
- Directed pedigree uses IBD2 + optional birth years; edge table under Details.
- Ambiguous edges stay undirected for user labeling.

---

## H — Ancient affinity

**Intent:** Closest ancient individuals/groups and a simple PCA neighborhood using
a reduced AADR-derived panel (or a small **demo panel** if AADR is not prepared).

**UI:** **PCA scatter** (reference points + “You” star) from the API `pca` payload,
then closest-individual / closest-group tables.

**Not claimed:** Descent from named royals or specific remains — see named-remains
highlights as affinity callouts only.

Setup details: [Open reference data](reference-data.md).

---

## I — Archaic affinity

**Intent:** Count / share of alleles matching a small open Neanderthal-informative
SNP list (`archaic_panel.json`).

**UI:** Summary counters + per-SNP hit table.

---

## J — Polygenic scores

**Intent:** Exploratory weighted allele scores from a local catalog.

**Default:** Shipped `prs_demo.json` (toy/demo weights for plumbing).

**Optional:** Place a converted PGS Catalog scoring JSON at
`data/reference/prs/catalog.json`.

**Not claimed:** Clinical risk prediction or diagnosis.

---

## Shared UI patterns

- Hub `/reports` uses **illustrated SVG tiles** (not tiny glyphs); sidebar shows
  the same art as thumbnails (`web/components/illustrations/`).
- `Disclaimer` / “About this result” collapse so predictions stay readable first.
- Primary sample from `SampleProvider` (top bar / settings).
- Hero stays brand-forward on `/`.

## Related docs

- [API reference](api.md)
- [Privacy and limits](privacy-and-limits.md)
- [Architecture](architecture.md)
