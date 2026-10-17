# Getting started

## Prerequisites

- Python 3.10+
- Node.js 18+ (for the report UI)
- Disk space for optional AADR downloads (can be several GB if you prepare a full panel)

## Install

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cd web && npm install && cd ..
```

Optional ancestry extra (heavier pins; not required — bundled AIM works without it):

```bash
pip install -e ".[ancestry]"
```

## Add genotype files

Place raw files in `data/` (this directory is gitignored):

```text
data/
  genome_Example_Person_v5_Full_….txt
  sample_meta.json          # optional; created by Settings
  reference/                # optional AADR / PRS downloads
```

Supported via the [`snps`](https://github.com/apriha/snps) library, including:

- 23andMe, AncestryDNA, FamilyTreeDNA, MyHeritage, LivingDNA
- VCF / compressed VCF
- Other formats `snps` can parse (CSV/TSV/ZIP when applicable)

GenoLens lists files matching `*.txt`, `*.csv`, `*.tsv`, `*.vcf`, `*.vcf.gz`,
`*.zip` under `data/` (not under `data/reference/`).

## Run the professional UI

**Terminal 1 — API (bind to localhost only):**

```bash
source .venv/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Equivalent:

```bash
genolens-api
```

**Terminal 2 — web:**

```bash
cd web
npm run dev
```

Open http://localhost:3000

1. Confirm the top bar shows your samples (not “API offline”).
2. Open **Settings → Samples & ages** to set the primary sample and optional birth years.
3. Open **View reports** and walk hubs A→J.

## First-time checklist

- [ ] At least one genotype file in `data/`
- [ ] API healthy: `curl -s http://127.0.0.1:8000/api/health`
- [ ] Samples listed: `curl -s http://127.0.0.1:8000/api/samples`
- [ ] Primary selected in the UI
- [ ] Relatives: pick candidates explicitly (never runs all-pairs over the whole folder)

## Production-ish local build (optional)

```bash
cd web
npm run build
npm start
```

Still requires the API on port 8000 (or set `NEXT_PUBLIC_API_BASE`).

## Tests

```bash
source .venv/bin/activate
pytest -q
```

## Next reading

- [Architecture](architecture.md)
- [Privacy and limits](privacy-and-limits.md)
- [API reference](api.md)
