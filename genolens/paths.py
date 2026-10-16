"""Repo-relative paths for samples and reference data."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DATA_DIR = REPO_ROOT / "data"
REFERENCE_DIR = DATA_DIR / "reference"
SHIPPED_DATA = PACKAGE_DIR / "data"

DEFAULT_PRIMARY_STEM = "genome_Saeid_Hosseinipoor_v5_Full_20220131131756"


def list_sample_files(directory: Path | None = None) -> list[Path]:
    """Return 23andMe-style text files under data/, sorted by name."""
    root = directory or DATA_DIR
    if not root.is_dir():
        return []
    return sorted(p for p in root.glob("*.txt") if p.is_file())


def sample_label(path: Path) -> str:
    """Human-readable label from a 23andMe filename."""
    name = path.stem
    if name.startswith("genome_"):
        name = name[len("genome_") :]
    for suffix in ("_v5_Full", "_v4_Full", "_Full"):
        idx = name.find(suffix)
        if idx > 0:
            name = name[:idx]
            break
    return name.replace("_", " ")


def default_primary(samples: list[Path] | None = None) -> Path | None:
    files = samples if samples is not None else list_sample_files()
    if not files:
        return None
    for path in files:
        if DEFAULT_PRIMARY_STEM in path.stem:
            return path
    return files[0]
