"""Repo-relative paths for samples and reference data."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DATA_DIR = REPO_ROOT / "data"
REFERENCE_DIR = DATA_DIR / "reference"
SHIPPED_DATA = PACKAGE_DIR / "data"

DEFAULT_PRIMARY_STEM = "genome_Saeid_Hosseinipoor_v5_Full_20220131131756"


_SAMPLE_GLOBS = ("*.txt", "*.csv", "*.tsv", "*.vcf", "*.vcf.gz", "*.zip")


def list_sample_files(directory: Path | None = None) -> list[Path]:
    """Return supported genotype files under data/, sorted by name.

    Formats follow what ``snps`` can parse (23andMe, AncestryDNA, FTDNA,
    MyHeritage, VCF, etc.). Reference dumps under ``data/reference/`` are skipped.
    """
    root = directory or DATA_DIR
    if not root.is_dir():
        return []
    found: list[Path] = []
    for pattern in _SAMPLE_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            if "reference" in path.parts:
                continue
            found.append(path)
    # de-dupe while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for path in sorted(found, key=lambda p: p.name.lower()):
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def sample_id(path: Path) -> str:
    """Stable id for API routes (filename stem)."""
    return path.stem


def sample_label(path: Path) -> str:
    """Human-readable label from a consumer DNA filename."""
    name = path.stem
    if name.startswith("genome_"):
        name = name[len("genome_") :]
    for suffix in ("_v5_Full", "_v4_Full", "_Full", "_AncestryDNA", "_MyHeritage"):
        idx = name.find(suffix)
        if idx > 0:
            name = name[:idx]
            break
    return name.replace("_", " ")


def resolve_sample(sample_key: str, directory: Path | None = None) -> Path | None:
    """Resolve an id or label to a genome path."""
    files = list_sample_files(directory)
    for path in files:
        if sample_id(path) == sample_key or sample_label(path) == sample_key:
            return path
    # allow absolute/relative path
    candidate = Path(sample_key)
    if candidate.is_file():
        return candidate
    return None


def default_primary(samples: list[Path] | None = None) -> Path | None:
    files = samples if samples is not None else list_sample_files()
    if not files:
        return None
    for path in files:
        if DEFAULT_PRIMARY_STEM in path.stem:
            return path
    return files[0]
