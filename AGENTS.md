# GenoLens agent instructions

Single source of rules for every coding agent in this repository. Pointer files
(`CLAUDE.md`, `.cursorrules`) only redirect here—put new rules in this file.

## Orientation

- GenoLens is a **local** DNA report app: raw genomes stay on disk; analysis does
  not upload to third parties.
- Python analysis lives in `genolens/`. The HTTP API is under `api/`. The
  professional report UI is under `web/` (Next.js). Streamlit (`genolens/app.py`)
  is a legacy entry point.
- Private genomes: `data/*.txt`. Reference downloads: `data/reference/`. Both are
  gitignored. Never stage, commit, or push them.
- Start with `README.md` for how to run the stack; deeper guides live in `docs/`.

## Working agreement

- Reading, searching, and read-only commands need no approval (`git status`,
  `git log`, `git diff`, unit tests, listing samples).
- Before changing files, Git state, syncing dependencies, or contacting an
  external network service, state a short plan when the session requires
  approval; approval covers that plan only. A request to discuss or plan is not
  approval to edit.
- Never push, force-push, merge into `main` on the remote, or change remotes
  unless the owner asks.
- Ask rather than guess names, paths, scope, interfaces, or commit boundaries.
  When the owner delegates a choice, say that it was delegated.

## Repository boundaries

- Tracked code: `genolens/`, `api/`, `web/`, `tests/`, `docs/`, and config.
- Never store credentials, tokens, or absolute machine-only secrets in tracked
  files. Local overrides belong in ignored config (for example `.env`).

### `docs/` vs `my-docs/` — do not mix

| Path | Purpose | Git |
|------|---------|-----|
| **`docs/`** | Shared product documentation for humans and teammates (architecture, API, runbooks). | **Tracked** — commit updates here. |
| **`my-docs/`** | Personal, machine-local agent knowledge base (sessions, decisions, private notes). | **Gitignored** — never stage, commit, copy into `docs/` or any tracked path, or upload. |

- Product docs belong only in `docs/` (and short pointers in `README.md`).
- Personal memory / update-my-docs output belongs only in `my-docs/`.
- Never move, mirror, or “promote” `my-docs/` content into `docs/` unless the owner
  explicitly asks to publish a specific non-private excerpt.
- When `my-docs/` exists, read `my-docs/machine-friendly/index.json` first for
  local context. Nothing a teammate needs may live only in `my-docs/`.

## Product rules

- Reports are **exploratory**, not medical advice, clinical diagnosis, or proof
  of descent from a named historical person.
- Never add a third-party genome-upload dependency to the default path.
- Compare / relatives: never auto-build an N×N matrix over every file in
  `data/`. The user picks one primary and selected candidates.
- Pedigree edges that need a generation direction must use IBD2 and/or
  user-supplied birth year / generation—not shared cM alone.

## Validation and handoff

- Run relevant tests after substantive changes (`pytest` for Python; API smoke
  tests when the API changes).
- Report the commands run, their results, and what was not verified (for
  example, no full AADR download or browser pass).
- Keep this file concise. Add a nested `AGENTS.md` only for a directory with
  genuinely different rules, and link it from here.
