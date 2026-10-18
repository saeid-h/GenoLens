# Development

## Repository map

```text
GenoLens/
  AGENTS.md          # single agent rules file
  README.md          # short runbook
  docs/              # this documentation set
  genolens/          # Python analysis package
  api/               # FastAPI app
  web/               # Next.js App Router UI
  tests/             # pytest
  data/              # local genomes (gitignored)
  pyproject.toml
```

## Agent / contributor rules

Read [`AGENTS.md`](../AGENTS.md) first. Highlights:

- Never commit genomes, `data/reference/`, or `my-docs/`.
- **`docs/` ≠ `my-docs/`:** public project docs for users go in `docs/` (tracked);
  the owner’s local private agent memory stays in `my-docs/` (ignored). Do not
  mix or mirror them.
- Never push unless the owner explicitly asks.
- Reports remain exploratory / non-clinical.
- Relatives must stay selection-driven; pedigree needs IBD2 and/or ages.
- Prefer asking over guessing names, paths, and commit boundaries.

Pointers: `CLAUDE.md`, `.cursorrules` → `AGENTS.md` only.

## Releases

- Baseline tag **`v0.0.0`** is released. Package / API version strings track the
  latest release (currently **`0.0.1`** / **`v0.0.1`** once that tag is cut).
- Branch new work from `main` (or the latest release tag). Prefer small,
  reviewable slices. See `AGENTS.md`.
- Never invent release tags or GitHub Releases without explicit owner consent.
  Pushing tags counts as a push.

## Python workflow

```bash
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Useful targets:

```bash
pytest tests/test_api_smoke.py -q
pytest tests/test_haplogroups_mt.py -q
pytest tests/test_compare_selected.py -q
```

Package data JSON is declared in `pyproject.toml` under
`[tool.setuptools.package-data]`.

Console scripts:

| Command | Entry |
|---------|-------|
| `genolens` | legacy Streamlit (`genolens.app:main`) |
| `genolens-api` | `api.main:run` (uvicorn on 127.0.0.1:8000) |

## Web workflow

```bash
cd web
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npx tsc --noEmit
```

API proxy: `web/next.config.mjs` rewrites `/api/*` → `127.0.0.1:8000`.

Brand tokens live in `web/app/globals.css` (teal `#0F6B5C`, coral accent,
warm canvas). Fonts: Fraunces (display) + Source Sans 3 (UI) via `next/font`.

## Adding a panel marker

1. Edit `genolens/data/health_panel.json` (or the relevant JSON).
2. Set `category` to the correct hub filter.
3. Add genotype → note map; keep non-diagnostic wording for health/carrier/pharma.
4. Add/adjust a pytest if behavior is subtle.
5. Hit the matching API route or report page.

## Adding an API route

1. Implement/reuse logic in `genolens/`.
2. Expose a thin handler in `api/main.py`.
3. Add a client helper in `web/lib/api.ts` if the UI needs it.
4. Extend `tests/test_api_smoke.py` (or a focused test module).

## Commit practice (this project)

- Commit after each logical stage when implementing multi-step work.
- Stage **named paths** only (never `git add -A`).
- Do **not** push without explicit owner consent.
- Match existing message style (short subject + why body; co-author trailers as used on `main`).

## Documentation updates

When behavior changes:

1. Update the relevant file under `docs/`.
2. Keep `docs/README.md` index accurate.
3. Keep root `README.md` short; link here for depth.

## Related docs

- [Architecture](architecture.md)
- [API reference](api.md)
- [Troubleshooting](troubleshooting.md)
