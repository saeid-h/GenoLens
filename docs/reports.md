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

**Intent:** Softmax AIM (Ancestry Informative Marker) affinity percentages across
continental / superpopulation-style labels.

**Not claimed:** Fine-grained country ethnicity, tribal identity, or legal ancestry.

**UI:** Stacked / bar percentages (`PercentBars`). If AIM markers are sparse on a
file, percentages are still exploratory — read markers-used notes in the payload.

**Upgrade path:** Denser open AISNP / Human Origins frequencies (still local).

---

## B — Haplogroups

**Intent:** Shallow paternal (Y) and maternal (mt) haplogroup **hints** from a
bundled defining-SNP tree.

**Important fix:** If a parent marker is missing on the chip, the walker
**soft-passes** and still tests children. Position-based MT markers (chrom+pos)
are used when rsIDs are absent on v5-class chips.

**UI:** Tip haplogroup, path (e.g. `N → R → U`), markers called/tested, note.

**Limits:** Microarrays rarely resolve fine subclades. “Unresolved” should only
appear when no derived alleles match — not merely because the root SNP is absent.

---

## C — Traits

**Intent:** Non-clinical trait markers (taste, pigmentation, earwax, muscle,
research associations) from the curated panel.

**UI:** Table columns **What this is** (plain summary) → gene → **Your DNA** →
**What your result means** (genotype-specific plain language).

---

## D — Wellness

**Intent:** Metabolism / alcohol / folate / sleep-adjacent markers
(`metabolism`, `wellness` categories).

**Copy:** Plain-language summaries; exploratory only — not nutrition or sleep advice.

---

## E — Pharmacogenetics

**Intent:** CYP / TPMT / SLCO1B1-style drug-gene markers with **strong caveats**.

**Never:** Recommend starting/stopping medication from GenoLens alone.

**UI:** Same plain-language hit table as Traits / Wellness.

---

## F — Health & carrier

**Intent:** Small redistributable carrier/health-style subset with non-diagnostic
wording (“not a diagnosis”, “seek clinical testing”).

**Categories:** `health`, `carrier` only (traits/pharma/wellness are separate hubs).

---

## G — DNA Relatives

See the dedicated guide: [Relatives and pedigree](relatives-and-pedigree.md).

Summary:

- Choose **primary** (settings) and **candidates** (relatives page).
- Compare selected pairs only.
- Directed pedigree uses IBD2 + optional birth years.
- Ambiguous edges stay undirected for user labeling.

---

## H — Ancient affinity

**Intent:** Closest ancient individuals/groups and a simple PCA neighborhood using
a reduced AADR-derived panel (or a small **demo panel** if AADR is not prepared).

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

- `Disclaimer` component on every hub.
- Primary sample from `SampleProvider` (top bar / settings).
- Cards used for scanning interactions; hero stays brand-forward on `/`.

## Related docs

- [API reference](api.md)
- [Privacy and limits](privacy-and-limits.md)
- [Architecture](architecture.md)
