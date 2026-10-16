"""Download and prepare a reduced AADR reference panel for ancient matching."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import numpy as np
import pandas as pd

from genolens.paths import REFERENCE_DIR

# Poseidon AADR archive package (v66 1240K). Large download — not committed.
AADR_PACKAGE = "AADR_v66_1240K"
AADR_ZIP_URL = (
    "https://server.poseidon-adna.org/zip_file/aadr-archive/"
    f"{AADR_PACKAGE}.zip"
)

PANEL_DIRNAME = "panel"
GENOTYPE_NPZ = "genotypes.npz"
ANNOTATION_CSV = "annotation.csv"
META_JSON = "panel_meta.json"


def reference_root(base: Path | None = None) -> Path:
    root = base or REFERENCE_DIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def panel_dir(base: Path | None = None) -> Path:
    return reference_root(base) / PANEL_DIRNAME


def panel_ready(base: Path | None = None) -> bool:
    d = panel_dir(base)
    return (d / GENOTYPE_NPZ).is_file() and (d / ANNOTATION_CSV).is_file()


def download_aadr(dest: Path | None = None, url: str = AADR_ZIP_URL) -> Path:
    """Download the AADR Poseidon zip into data/reference/."""
    root = reference_root(dest)
    zip_path = root / f"{AADR_PACKAGE}.zip"
    if zip_path.is_file() and zip_path.stat().st_size > 1_000_000:
        return zip_path
    urlretrieve(url, zip_path)  # noqa: S310 — intentional user-triggered download
    return zip_path


def extract_aadr(zip_path: Path, dest: Path | None = None) -> Path:
    root = reference_root(dest)
    out = root / AADR_PACKAGE
    if out.is_dir() and any(out.iterdir()):
        return out
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(root)
    # Poseidon packages may nest one level
    if not out.is_dir():
        candidates = [p for p in root.iterdir() if p.is_dir() and "AADR" in p.name]
        if candidates:
            return candidates[0]
    return out


def _find_eigenstrat(package_dir: Path) -> tuple[Path, Path, Path] | None:
    """Locate .geno/.snp/.ind (or packed equivalents) under a Poseidon package."""
    geno = next(package_dir.rglob("*.geno"), None)
    snp = next(package_dir.rglob("*.snp"), None)
    ind = next(package_dir.rglob("*.ind"), None)
    if geno and snp and ind:
        return geno, snp, ind
    return None


def _parse_snp_table(snp_path: Path, max_snps: int | None = None) -> pd.DataFrame:
    rows = []
    with snp_path.open(encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if max_snps is not None and i >= max_snps:
                break
            parts = line.split()
            if len(parts) < 5:
                continue
            # EIGENSTRAT: ID chrom genetic_pos physical_pos ref alt (sometimes)
            snp_id = parts[0]
            chrom = parts[1]
            pos = int(float(parts[3]))
            alleles = parts[4:]
            ref = alleles[0] if alleles else "N"
            alt = alleles[1] if len(alleles) > 1 else "N"
            rows.append(
                {
                    "snp_id": snp_id,
                    "chrom": chrom,
                    "pos": pos,
                    "ref": ref.upper(),
                    "alt": alt.upper(),
                }
            )
    return pd.DataFrame(rows)


def _is_strand_ambiguous(ref: str, alt: str) -> bool:
    pair = {ref.upper(), alt.upper()}
    return pair in ({"A", "T"}, {"C", "G"})


def _parse_ind_table(ind_path: Path) -> pd.DataFrame:
    rows = []
    with ind_path.open(encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            parts = line.split()
            if len(parts) < 3:
                continue
            rows.append(
                {
                    "sample_idx": i,
                    "genetic_id": parts[0],
                    "sex": parts[1],
                    "group": parts[2],
                }
            )
    return pd.DataFrame(rows)


def _read_geno_matrix(geno_path: Path, n_snps: int, n_inds: int) -> np.ndarray:
    """Read EIGENSTRAT geno: rows=SNPs, cols=individuals, chars 0/1/2/9."""
    # Prefer packed geno if file is binary and small relative — for hobby use we
    # stream text geno. If file is huge, caller should pre-subset.
    matrix = np.full((n_snps, n_inds), 9, dtype=np.uint8)
    with geno_path.open("rb") as fh:
        for i in range(n_snps):
            line = fh.readline()
            if not line:
                break
            # strip newline
            raw = line.rstrip(b"\r\n")
            # packed geno: each byte encodes multiple samples — detect by length
            if len(raw) == n_inds and all(c in b"0129" for c in raw[: min(20, len(raw))]):
                matrix[i, : len(raw)] = np.frombuffer(raw[:n_inds], dtype=np.uint8) - ord("0")
            else:
                # fallback: decode as latin-1 text digits
                text = raw.decode("latin-1")
                for j, ch in enumerate(text[:n_inds]):
                    if ch in "0129":
                        matrix[i, j] = ord(ch) - ord("0")
    return matrix


def build_demo_panel(
    out_dir: Path | None = None,
    n_snps: int = 200,
    n_samples: int = 40,
    seed: int = 42,
) -> Path:
    """Write a tiny synthetic panel for offline tests and first-run demos."""
    rng = np.random.default_rng(seed)
    dest = panel_dir(out_dir)
    dest.mkdir(parents=True, exist_ok=True)

    snp_ids = [f"rsDEMO{i:05d}" for i in range(n_snps)]
    chroms = [str((i % 22) + 1) for i in range(n_snps)]
    positions = [1000 + i * 1000 for i in range(n_snps)]
    # genotypes: 0/1/2 dosage of alt; 9 = missing. Prefer non-ambiguous alleles.
    alleles = [("A", "G"), ("C", "T"), ("G", "A"), ("T", "C")]
    refs = [alleles[i % 4][0] for i in range(n_snps)]
    alts = [alleles[i % 4][1] for i in range(n_snps)]

    groups = ["Iran_IronAge", "Egypt_Abusir", "Anatolia_N", "Steppe_MLBA", "Iceman_proxy"]
    countries = ["Iran", "Egypt", "Turkey", "Russia", "Italy"]
    dates = [-800, -500, -6500, -1500, -3300]
    ann_rows = []
    for j in range(n_samples):
        g = groups[j % len(groups)]
        ann_rows.append(
            {
                "sample_idx": j,
                "genetic_id": f"{g}_{j:03d}",
                "sex": "U",
                "group": g,
                "country": countries[j % len(countries)],
                "date": dates[j % len(dates)],
            }
        )
    annotation = pd.DataFrame(ann_rows)

    # Cluster genotypes slightly by group so distance ranking is meaningful
    geno = np.zeros((n_snps, n_samples), dtype=np.uint8)
    for j in range(n_samples):
        center = (j % len(groups)) * 0.4
        probs = np.clip(rng.random(n_snps) + center - 0.5, 0, 1)
        geno[:, j] = np.where(probs > 0.7, 2, np.where(probs > 0.35, 1, 0)).astype(np.uint8)
        # sprinkle missing
        miss = rng.random(n_snps) < 0.05
        geno[miss, j] = 9

    snp_table = pd.DataFrame(
        {
            "snp_id": snp_ids,
            "chrom": chroms,
            "pos": positions,
            "ref": refs,
            "alt": alts,
        }
    )

    np.savez_compressed(
        dest / GENOTYPE_NPZ,
        genotypes=geno,
        snp_ids=np.array(snp_ids),
        positions=np.array(positions),
        chroms=np.array(chroms),
        refs=np.array(refs),
        alts=np.array(alts),
    )
    annotation.to_csv(dest / ANNOTATION_CSV, index=False)
    snp_table.to_csv(dest / "snps.csv", index=False)
    meta = {
        "source": "synthetic_demo",
        "n_snps": n_snps,
        "n_samples": n_samples,
        "citation": "Demo panel only — replace with AADR v66 after download/prepare.",
        "aadr_package": AADR_PACKAGE,
        "aadr_url": AADR_ZIP_URL,
    }
    (dest / META_JSON).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dest


def prepare_panel_from_eigenstrat(
    package_dir: Path,
    user_positions: set[tuple[str, int]] | None = None,
    max_snps: int = 50_000,
    max_samples: int | None = 2000,
    out_dir: Path | None = None,
) -> Path:
    """Intersect EIGENSTRAT AADR with user SNP positions; drop A/T and C/G."""
    found = _find_eigenstrat(package_dir)
    if not found:
        raise FileNotFoundError(f"No EIGENSTRAT .geno/.snp/.ind under {package_dir}")
    geno_path, snp_path, ind_path = found

    snps = _parse_snp_table(snp_path)
    snps = snps[~snps.apply(lambda r: _is_strand_ambiguous(r["ref"], r["alt"]), axis=1)].reset_index(drop=True)

    if user_positions:
        mask = snps.apply(lambda r: (str(r["chrom"]), int(r["pos"])) in user_positions, axis=1)
        snps = snps[mask].reset_index(drop=True)

    if len(snps) > max_snps:
        snps = snps.iloc[:: max(1, len(snps) // max_snps)].head(max_snps).reset_index(drop=True)

    inds = _parse_ind_table(ind_path)
    if max_samples and len(inds) > max_samples:
        inds = inds.head(max_samples).reset_index(drop=True)

    # Re-read only selected SNP rows — for simplicity reload full then index
    # (full AADR is large; users should run prepare once with max_snps).
    full_snps = _parse_snp_table(snp_path)
    keep_idx = full_snps.index[full_snps["snp_id"].isin(snps["snp_id"])].tolist()
    n_inds_full = len(_parse_ind_table(ind_path))
    full_geno = _read_geno_matrix(geno_path, n_snps=len(full_snps), n_inds=n_inds_full)
    geno = full_geno[np.array(keep_idx)][:, : len(inds)]

    dest = panel_dir(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    annotation = inds.copy()
    if "country" not in annotation.columns:
        annotation["country"] = ""
    if "date" not in annotation.columns:
        annotation["date"] = ""

    np.savez_compressed(
        dest / GENOTYPE_NPZ,
        genotypes=geno.astype(np.uint8),
        snp_ids=snps["snp_id"].to_numpy(),
        positions=snps["pos"].to_numpy(),
        chroms=snps["chrom"].astype(str).to_numpy(),
        refs=snps["ref"].astype(str).to_numpy(),
        alts=snps["alt"].astype(str).to_numpy(),
    )
    annotation.to_csv(dest / ANNOTATION_CSV, index=False)
    snps.to_csv(dest / "snps.csv", index=False)
    meta = {
        "source": AADR_PACKAGE,
        "n_snps": int(len(snps)),
        "n_samples": int(len(inds)),
        "citation": (
            "Mallick, S., & Reich, D. Allen Ancient DNA Resource (AADR). "
            "Harvard Dataverse. Also Mallick et al. 2024, Scientific Data."
        ),
        "aadr_package": AADR_PACKAGE,
        "aadr_url": AADR_ZIP_URL,
    }
    (dest / META_JSON).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dest


def load_panel(base: Path | None = None) -> dict[str, Any]:
    d = panel_dir(base)
    if not panel_ready(base):
        raise FileNotFoundError(
            f"No prepared panel in {d}. Run build_demo_panel() or download/prepare AADR."
        )
    data = np.load(d / GENOTYPE_NPZ, allow_pickle=True)
    annotation = pd.read_csv(d / ANNOTATION_CSV)
    meta: dict[str, Any] = {}
    meta_path = d / META_JSON
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return {
        "genotypes": data["genotypes"],
        "snp_ids": data["snp_ids"].astype(str),
        "positions": data["positions"],
        "chroms": data["chroms"].astype(str),
        "refs": data["refs"].astype(str),
        "alts": data["alts"].astype(str),
        "annotation": annotation,
        "meta": meta,
        "dir": d,
    }


def ensure_panel(base: Path | None = None, use_demo_if_missing: bool = True) -> Path:
    if panel_ready(base):
        return panel_dir(base)
    if use_demo_if_missing:
        return build_demo_panel(base)
    raise FileNotFoundError("Reference panel missing")
