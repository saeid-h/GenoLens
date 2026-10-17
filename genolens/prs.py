"""Exploratory polygenic scores from a local weight file (PGS Catalog-compatible shape)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import REFERENCE_DIR, SHIPPED_DATA


def load_prs_catalog(path: Path | None = None) -> dict[str, Any]:
    """Load demo weights, or a downloaded catalog JSON under data/reference/prs/."""
    if path is not None:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    downloaded = REFERENCE_DIR / "prs" / "catalog.json"
    if downloaded.is_file():
        with downloaded.open(encoding="utf-8") as fh:
            return json.load(fh)
    with (SHIPPED_DATA / "prs_demo.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def _dosage(genotype: str | None, effect_allele: str) -> float:
    if not genotype or genotype in {"--", "nan"}:
        return 0.0
    return float(genotype.upper().count(effect_allele.upper()))


def score_prs(snps: SNPs, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    catalog = catalog or load_prs_catalog()
    genotypes = genotype_lookup(snps)
    results = []
    for score in catalog.get("scores", []):
        raw = 0.0
        used = 0
        missing = 0
        for var in score.get("variants", []):
            geno = genotypes.get(var["rsid"])
            if geno is None:
                missing += 1
                continue
            used += 1
            raw += _dosage(geno, var["effect_allele"]) * float(var["weight"])
        results.append(
            {
                "id": score.get("id"),
                "trait": score.get("trait"),
                "citation": score.get("citation", ""),
                "raw_score": raw,
                "variants_used": used,
                "variants_missing": missing,
            }
        )
    return {
        "disclaimer": catalog.get("disclaimer", ""),
        "source": "local demo or data/reference/prs/catalog.json",
        "scores": results,
        "pgs_catalog_hint": (
            "Download open scoring files from https://www.pgscatalog.org/ and place a "
            "converted catalog.json under data/reference/prs/ for richer scores."
        ),
    }
