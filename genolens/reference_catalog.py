"""Helpers to download open reference catalogs once into data/reference/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from genolens.paths import REFERENCE_DIR

PGS_CATALOG_REST = "https://www.pgscatalog.org/rest/"


def ensure_reference_dirs() -> dict[str, Path]:
    paths = {
        "root": REFERENCE_DIR,
        "aadr": REFERENCE_DIR / "aadr",
        "prs": REFERENCE_DIR / "prs",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def pgs_catalog_status() -> dict[str, Any]:
    """Describe local PRS catalog availability (no forced download)."""
    paths = ensure_reference_dirs()
    local = paths["prs"] / "catalog.json"
    return {
        "local_catalog": str(local) if local.is_file() else None,
        "rest_base": PGS_CATALOG_REST,
        "hint": (
            "Place a converted PGS Catalog scoring JSON at data/reference/prs/catalog.json, "
            "or use the shipped demo weights in genolens/data/prs_demo.json."
        ),
    }


def fetch_pgs_score_metadata(pgs_id: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch metadata for one PGS id (annotation only; does not upload genomes)."""
    url = f"{PGS_CATALOG_REST}score/{pgs_id}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def aadr_download_hint() -> dict[str, str]:
    return {
        "poseidon": "https://server.poseidon-adna.org/explorer/aadr-archive",
        "dataverse": "https://doi.org/10.7910/DVN/FFIDCW",
        "local_dir": str(REFERENCE_DIR / "aadr"),
        "note": "Download AADR once into data/reference/aadr/, then run genolens.reference prepare helpers.",
    }
