# GenoLens

Local, private viewer for 23andMe raw data. Explore trait / pharmacogenetic markers, pairwise relatedness, broad ancestry, and affinity to ancient genomes. **Nothing is uploaded.**

## Limits (read these)

- **Not medical advice.** Microarray data covers a tiny fraction of the genome. Panel notes are exploratory literature summaries, not diagnoses.
- **Ancient matches are population affinity**, not proof you descend from a named king or pharaoh. Royal Egyptian and Achaemenid genomes are not publicly released. Ancient samples are low-coverage; IBD segment matching like modern relative-finder tools does not apply the same way.

## Setup

```bash
cd /path/to/GenoLens
python3.12 -m venv .venv   # Python 3.10+ required
source .venv/bin/activate
pip install -e ".[dev]"
```

Superpopulation calls use `snps.predict_ancestry` when available. The older `ezancestry` package pins `pandas<2` and conflicts with Streamlit, so it is an optional extra (`pip install -e ".[ancestry]"`) best used in a separate environment.

Place your 23andMe raw exports as `data/*.txt` (already gitignored). The app lists those files and defaults the primary sample to the Saeid Hosseinipoor v5 export when present.

## Run

```bash
streamlit run genolens/app.py
```

Pages: **Overview**, **Health**, **Compare**, **Ancestry**, **Ancient**.

## Ancient reference (AADR)

1. First run can create a **synthetic demo panel** so the Ancient page works offline.
2. For real matches, download **AADR v66 1240K** from the [Poseidon AADR archive](https://server.poseidon-adna.org/explorer/aadr-archive) into `data/reference/` (gitignored; ~tens of thousands of samples).
3. Prepare a reduced panel intersecting positions present on your v5 chip, dropping strand-ambiguous A/T and C/G SNPs, then score allele-sharing distance and project yourself onto a PCA fit from the reference only.

Helper entry points live in `genolens.reference` (`download_aadr`, `extract_aadr`, `prepare_panel_from_eigenstrat`, `build_demo_panel`).

### Citation

When using AADR data, cite:

1. Mallick, S., & Reich, D. — Allen Ancient DNA Resource (AADR), Harvard Dataverse (version you download).
2. Mallick et al. (2024), *The Allen Ancient DNA Resource (AADR): a curated compendium of ancient human genomes*, Scientific Data.

## Tests

```bash
pytest
```

Tests use tiny synthetic genotype files only — never the private genomes under `data/`.

## Stack

- [`snps`](https://github.com/apriha/snps) — load 23andMe files
- [`lineage`](https://github.com/apriha/lineage) — shared segments / relatedness
- Optional `genolens[ancestry]` (`snps[ezancestry]`) — 1000 Genomes superpopulation call. Not in the default install: ezancestry pins pandas 1.x and conflicts with Streamlit on Python 3.9.
- `scikit-learn` — PCA projection for ancient affinity
- Streamlit — local UI
