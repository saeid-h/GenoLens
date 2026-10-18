# Contributing to GenoLens

Thanks for your interest. GenoLens is a **local** DNA report app: raw genomes
stay on disk and analysis does not upload them to third parties. Reports are
**exploratory**, not medical advice or clinical diagnosis.

## Before you start

1. Read [`README.md`](README.md) for setup and how to run the stack.
2. Read [`AGENTS.md`](AGENTS.md) for repository rules (privacy, relatives,
   releases, commits).
3. Skim [`docs/development.md`](docs/development.md) for the Python / web
   workflow and [`docs/privacy-and-limits.md`](docs/privacy-and-limits.md).

## Privacy (non-negotiable)

Never stage, commit, or open a PR that includes:

- Genotype files under `data/` (for example `data/*.txt`)
- `data/reference/` downloads
- `data/sample_meta.json`
- `my-docs/` (owner-private; gitignored)
- `.env`, credentials, tokens, or absolute machine-only secrets
- Build junk (`web/node_modules/`, `web/.next/`, `*.tsbuildinfo`)

Do not attach genotype data to issues or PRs. Describe problems with
environment, steps, and redacted logs only.

## Product constraints

- Do not add a third-party genome-upload dependency on the default path.
- Relatives / compare must stay **selection-driven** (primary + chosen
  candidates). Never auto-build an N×N matrix over every file in `data/`.
- Pedigree edges that need a generation direction must use IBD2 and/or
  user-supplied birth year / generation—not shared cM alone.
- User-facing copy stays exploratory / non-clinical.

## Development workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd web && npm install && cd ..
pytest -q
```

API: `uvicorn api.main:app --host 127.0.0.1 --port 8000`  
Web: `cd web && npm run dev` → http://localhost:3000

## Pull requests

1. Branch from `main` (baseline `v0.0.0` and later tags). Prefer small,
   reviewable slices.
2. Stage **named paths** only (no `git add -A` / `git add .`).
3. Run relevant tests (`pytest`; API smoke when the API changes).
4. Update `docs/` when behavior changes. Do not put public docs only in
   `my-docs/`.
5. Fill out the PR template checklist.

## Code of conduct

Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Security

See [`SECURITY.md`](SECURITY.md) for how to report vulnerabilities privately.
