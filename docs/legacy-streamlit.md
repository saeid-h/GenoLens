# Legacy Streamlit UI

The original GenoLens interface lives in `genolens/app.py`. It remains available
for spot checks, but the **primary product UX** is the Next.js report app.

## Run

```bash
source .venv/bin/activate
streamlit run genolens/app.py
```

Or:

```bash
genolens
```

## What still works

- Loading samples from `data/`
- Ancestry, haplogroups, health-panel views
- Relatedness tools (prefer the new selection-driven web Relatives hub for large libraries)
- Ancient affinity helpers when reference data is present

## What to prefer in the new UI

| Concern | Prefer |
|---------|--------|
| Report hub navigation A–J | Next.js `/reports` |
| Primary × candidates compare | Next.js Relatives + `POST /api/compare` |
| Directed pedigree with ages | Next.js + `sample_meta.json` |
| Brand / layout | Next.js shell |

## Deprecation stance

Streamlit is **temporary legacy**, not deleted. New features should land in
`genolens/` (shared) + `api/` + `web/` first. Only mirror into Streamlit when
needed for parity during transition.

## Related docs

- [Getting started](getting-started.md)
- [Architecture](architecture.md)
