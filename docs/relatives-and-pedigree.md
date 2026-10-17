# Relatives and pedigree

This hub replaces the old “compare every file to every file” Streamlit behavior.

## Why selection-driven compare?

`compare_all_pairs` over every `data/*.txt` is **O(n²)** and becomes unusable as
the library grows (tens to ~100 files). GenoLens therefore requires:

1. One **primary** sample (Settings).
2. Explicit multi-select **candidates**.
3. Action: compare / build tree → API runs only those pairs.

Optional triangulation among a **small** selected set (including primary) is
capped (≤ 8 people) inside `POST /api/family-tree`.

## Shared cM is symmetric

Total half-identical region (HIR) cM does **not** encode generation. Parent–child
and full siblings can both land in high bands. Without more signal, a heuristic
can mis-place a grandparent as a “sibling.”

## Classification signals

Approximate ISOGG-style bands used in code (`genolens.relatedness`):

| Band | Shared cM (HIR) | Default edge kind |
|------|-----------------|-------------------|
| Parent/child range | ≥ 3400 | `parent_child` (unless high IBD2 → sibling) |
| Sibling range | 2200–3400 | `sibling` |
| Close relative | ≥ 1300 | `close_relative` |
| Distant | > 0 | `distant` |
| Unrelated | 0 | `unrelated` |

### IBD2 (two-chrom sharing)

Full siblings share substantial **IBD2**; parent–child pairs share almost none.

- High IBD2 with parent/child-range total cM → treat as **sibling**.
- Low/unknown IBD2 with ≥ 3400 cM → **parent_child**.
- In the classic sibling cM band, GenoLens keeps **sibling** even when IBD2 is
  missing (0), because zero often means “not measured” in synthetic/tests and
  parent–child almost never sits in 2200–3400.

### Ages / birth year

Stored in gitignored `data/sample_meta.json`. When two people in a parent/child
band differ by ≥ ~15 years, the older birth year becomes the parent end of a
**directed** edge.

### Triangulation

If A–B and A–C look parent–child and B–C looks sibling, B and C are treated as
children of A when the graph supports it (nuclear-family pass in `infer_pedigree`).

### Ambiguity

If direction is unclear, GenoLens emits an **undirected** edge and a note asking
the user to set relationship / ages. It must **not** invent “grandma as sister.”

## UI workflow

1. Settings → choose primary; optionally enter birth years.
2. Reports → DNA Relatives → select candidates (chips with birth-year badges).
3. Compare selected → pedigree hero, then relationship cards:
   - **With you** — primary × each candidate
   - **Among selected relatives** — candidate × candidate (e.g. mother ×
     grandmother) when the selected set has 3–8 people
4. Edge table + ASCII pedigree under **Details**.

Mother–grandmother (and any other candidate pair) is examined automatically for
tree orientation whenever both are in the selected set; GenoLens never matrices
every file in `data/`.

## API

- `POST /api/compare` — primary × candidates only.
- `POST /api/family-tree` — all pairs among the small selected set (≤8) +
  `pedigree` graph. Response `pairs` includes candidate × candidate.

Details: [API reference](api.md).

## Roles and sex

When SNP-derived sex is known for two co-parents, roles become Mother/Father.
Otherwise Parent A / Parent B — GenoLens does not invent genders.

## Related docs

- [Report hubs](reports.md) (hub G)
- [Privacy and limits](privacy-and-limits.md)
- [Data and formats](data-and-formats.md)
