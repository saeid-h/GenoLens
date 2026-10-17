"""Exploratory polygenic scores from a local weight file (PGS Catalog-compatible shape)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import REFERENCE_DIR, SHIPPED_DATA


def load_prs_catalog(path: Path | None = None) -> tuple[dict[str, Any], str]:
    """Load catalog JSON and return ``(catalog, mode)`` where mode is ``demo`` or ``catalog``."""
    if path is not None:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data, str(data.get("mode") or "catalog")
    downloaded = REFERENCE_DIR / "prs" / "catalog.json"
    if downloaded.is_file():
        with downloaded.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data, str(data.get("mode") or "catalog")
    with (SHIPPED_DATA / "prs_demo.json").open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data, str(data.get("mode") or "demo")


def _dosage(genotype: str | None, effect_allele: str) -> float:
    if not genotype or genotype in {"--", "nan"}:
        return 0.0
    return float(genotype.upper().count(effect_allele.upper()))


def _coverage_label(used: int, total: int) -> str:
    if total <= 0:
        return "No variants in this score definition."
    frac = used / total
    if used == 0:
        return "None of these SNPs were called on your file — score is empty."
    if frac < 0.4:
        return "Low coverage — treat this number as almost noise."
    if frac < 0.8:
        return "Partial coverage — direction may be weakly informative only."
    return "Most panel SNPs were called on your file."


def _band(fraction_of_max: float | None, used: int, total: int) -> str:
    if used == 0 or total == 0 or fraction_of_max is None:
        return "unavailable"
    if fraction_of_max < 0.25:
        return "lower end of this tiny panel"
    if fraction_of_max < 0.55:
        return "middle of this tiny panel"
    if fraction_of_max < 0.8:
        return "upper-middle of this tiny panel"
    return "upper end of this tiny panel"


def score_prs(snps: SNPs, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    if catalog is None:
        catalog, mode = load_prs_catalog()
    else:
        mode = str(catalog.get("mode") or "catalog")

    genotypes = genotype_lookup(snps)
    results = []
    for score in catalog.get("scores", []):
        variants = score.get("variants", [])
        raw = 0.0
        used = 0
        missing = 0
        max_if_all_effect = 0.0
        detail: list[dict[str, Any]] = []
        for var in variants:
            w = float(var["weight"])
            max_if_all_effect += 2.0 * abs(w)
            geno = genotypes.get(var["rsid"])
            if geno is None:
                missing += 1
                detail.append(
                    {
                        "rsid": var["rsid"],
                        "effect_allele": var["effect_allele"],
                        "weight": w,
                        "genotype": None,
                        "dosage": None,
                        "contribution": 0.0,
                        "present": False,
                    }
                )
                continue
            used += 1
            dosage = _dosage(geno, var["effect_allele"])
            contrib = dosage * w
            raw += contrib
            detail.append(
                {
                    "rsid": var["rsid"],
                    "effect_allele": var["effect_allele"],
                    "weight": w,
                    "genotype": geno,
                    "dosage": dosage,
                    "contribution": contrib,
                    "present": True,
                }
            )

        total = used + missing
        frac = (raw / max_if_all_effect) if max_if_all_effect > 0 and used > 0 else None
        coverage_pct = (100.0 * used / total) if total else 0.0
        band = _band(frac, used, total)
        is_demo = mode == "demo"

        if used == 0:
            readout = "No SNPs from this score were called — nothing to interpret."
        elif is_demo:
            readout = (
                f"Demo allele-sum on this chip: {raw:.4f} "
                f"({band}; {used}/{total} SNPs called). "
                "Not a real trait measurement."
            )
        else:
            readout = (
                f"Weighted allele sum: {raw:.4f} "
                f"({used}/{total} scoring SNPs called). "
                "Exploratory only — not a clinical risk or diagnosis."
            )

        results.append(
            {
                "id": score.get("id"),
                "trait": score.get("trait"),
                "trait_plain": score.get("trait_plain") or score.get("trait"),
                "what_it_is": score.get("what_it_is")
                or "A weighted sum of effect alleles across a SNP list for one trait.",
                "what_it_is_not": score.get("what_it_is_not")
                or "Not a diagnosis, not medical advice, and not a precise personal prediction.",
                "citation": score.get("citation", ""),
                "raw_score": raw,
                "max_score_if_all_effect_alleles": max_if_all_effect,
                "fraction_of_panel_max": frac,
                "panel_band": band,
                "variants_used": used,
                "variants_missing": missing,
                "variants_total": total,
                "coverage_percent": coverage_pct,
                "coverage_note": _coverage_label(used, total),
                "readout": readout,
                "is_demo": is_demo,
                "variants": detail,
            }
        )

    return {
        "disclaimer": catalog.get("disclaimer", ""),
        "how_to_read": catalog.get("how_to_read")
        or (
            "A polygenic score adds many small SNP effects into one number. "
            "GenoLens shows the raw weighted sum and how many SNPs were actually on your chip."
        ),
        "mode": mode,
        "is_demo": mode == "demo",
        "source": (
            "shipped demo weights (genolens/data/prs_demo.json)"
            if mode == "demo"
            else "data/reference/prs/catalog.json"
        ),
        "scores": results,
        "pgs_catalog_hint": (
            "For open, literature-linked scores: download from https://www.pgscatalog.org/ "
            "and place a converted catalog.json under data/reference/prs/. "
            "Until then GenoLens uses a tiny demo panel so the hub is understandable, not clinical."
        ),
    }
