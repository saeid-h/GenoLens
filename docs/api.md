# API reference

Base URL (local): `http://127.0.0.1:8000`

Interactive docs: http://127.0.0.1:8000/docs

CORS allows `http://localhost:3000` and `http://127.0.0.1:3000`.

Unless noted, JSON responses may include a `disclaimer` string.

---

## Health

### `GET /api/health`

Liveness probe.

```json
{ "status": "ok", "service": "genolens" }
```

---

## Samples and metadata

### `GET /api/samples`

Lists genotype files under `data/`.

```json
{
  "disclaimer": "…",
  "default_primary_id": "genome_…",
  "samples": [
    {
      "id": "genome_…",
      "label": "Saeid Hosseinipoor",
      "filename": "genome_….txt",
      "meta": { "birth_year": 1980 }
    }
  ]
}
```

### `GET /api/samples/meta`

Returns the full `data/sample_meta.json` document (or `{ "samples": {} }`).

### `PUT /api/samples/{sample_key}/meta`

Body (all fields optional):

```json
{
  "birth_year": 1952,
  "generation": "grandparent",
  "display_name": "Farideh"
}
```

Empty / null fields clear stored keys. `{sample_key}` may be sample **id** or **label**.

### `GET /api/samples/{sample_key}/overview`

Genome summary + meta. Includes `count`, `sex`, `build`, `source`, `chip`, etc.

---

## Ancestry and haplogroups

### `GET /api/samples/{sample_key}/ancestry`

AIM-based continental affinity. Typical fields from `predict_ancestry(...).as_dict()`:

- `percentages` — label → percent
- `method` / notes about AIM vs unavailable
- markers used when provided by the engine

### `GET /api/samples/{sample_key}/haplogroups`

```json
{
  "id": "genome_…",
  "Y": {
    "lineage": "Y",
    "haplogroup": "BT",
    "path": ["BT"],
    "markers_tested": 13,
    "markers_called": 9,
    "note": "…"
  },
  "mt": {
    "lineage": "mt",
    "haplogroup": "U",
    "path": ["N", "R", "U"],
    "markers_tested": 12,
    "markers_called": 6,
    "note": "…"
  }
}
```

Missing parent SNPs on the chip are **soft-passed** so child markers can still resolve a macrohaplogroup.

---

## Panel hubs (traits / wellness / pharma / health)

### `GET /api/samples/{sample_key}/traits`

### `GET /api/samples/{sample_key}/wellness`

### `GET /api/samples/{sample_key}/pharmacogenetics`

### `GET /api/samples/{sample_key}/health`

Shared response shape:

```json
{
  "disclaimer": "…",
  "hub": "traits",
  "id": "genome_…",
  "markers_called": 12,
  "markers_total": 20,
  "hits": [
    {
      "rsid": "rs713598",
      "gene": "TAS2R38",
      "category": "trait",
      "summary": "…",
      "genotype": "CG",
      "note": "…",
      "source": "…",
      "present": true
    }
  ]
}
```

Category filters (`genolens.health`):

| Hub | Categories |
|-----|------------|
| traits | `trait` |
| wellness | `metabolism`, `wellness` |
| pharmacogenetics | `pharmacogenetics` |
| health | `health`, `carrier` |

---

## Relatives

### `POST /api/compare`

Runs **only** `primary × each candidate` (never the whole `data/` folder).

```json
{
  "primary_id": "genome_A…",
  "candidate_ids": ["genome_B…", "genome_C…"]
}
```

Response:

```json
{
  "primary_id": "…",
  "primary_label": "…",
  "pairs": [
    {
      "sample_a": "…",
      "sample_b": "…",
      "shared_cm": 3500.0,
      "shared_segments": 42,
      "ibd2_cm": 12.0,
      "relationship": "Parent/child range …",
      "error": null
    }
  ]
}
```

### `POST /api/family-tree`

Same body shape as compare. Behavior:

1. Compare primary × candidates.
2. If the selected set has 3–8 people, also compute pairs among the full selected set (capped) for triangulation.
3. Load SNP-derived sex + `birth_year` from meta.
4. Run `infer_pedigree` → directed edges where possible.

Response includes `pairs` and `pedigree`:

```json
{
  "pedigree": {
    "nodes": [
      { "label": "Farideh", "generation": 0, "role": "Mother", "sex": "female" }
    ],
    "edges": [
      {
        "source": "Farideh",
        "target": "Saeid",
        "kind": "parent_child",
        "shared_cm": 3500,
        "directed": true,
        "confidence": "high",
        "note": "…"
      }
    ],
    "notes": [],
    "ascii_tree": "…"
  }
}
```

Undirected dashed edges mean: set birth years or manually label the relationship.

---

## Ancient / archaic / PRS

### `GET /api/samples/{sample_key}/ancient`

Ensures a panel exists (prepares demo panel if AADR-reduced panel is missing). Returns:

- `status` — panel readiness
- `ranked.individuals` / `ranked.groups`
- `pca` — user point + sample of reference points
- `named_remains` — optional highlight list (affinity, not descent proof)

### `GET /api/samples/{sample_key}/archaic`

Archaic-informative allele sharing summary + per-SNP hits.

### `GET /api/samples/{sample_key}/prs`

Exploratory scores from `data/reference/prs/catalog.json` if present, else shipped `prs_demo.json`.

### `GET /api/reference/status`

Non-genome status for AADR hints and PGS catalog locality.

---

## Errors

| Code | When |
|------|------|
| 404 | Unknown sample / candidate id |
| 422 | Invalid body validation failure |
| 500 | Unexpected analysis error (check API logs) |

---

## Client usage (web)

`web/lib/api.ts` wraps these routes. With `npm run dev`, browser calls go to
`/api/...` and Next rewrites them to port 8000.

Override with:

```bash
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev
```

## Related docs

- [Relatives and pedigree](relatives-and-pedigree.md)
- [Report hubs](reports.md)
- [Getting started](getting-started.md)
