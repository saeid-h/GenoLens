## Summary

<!-- What changed and why (short). -->

## Checklist

- [ ] Description explains the **why**, not only the what
- [ ] Relevant tests run (`pytest` and/or API smoke when the API changes)
- [ ] **No private data staged** — no `data/*.txt`, `data/reference/`, `data/sample_meta.json`, `my-docs/`, `.env`, or credentials
- [ ] Named paths only when staging (no `git add -A` / `git add .`)
- [ ] `docs/` updated if user-facing or API behavior changed
- [ ] User-facing copy stays exploratory / non-clinical
- [ ] Relatives remain selection-driven (no auto N×N over all of `data/`)
- [ ] No new third-party genome-upload dependency on the default path

## Test plan

<!-- Commands run and what was not verified. -->
