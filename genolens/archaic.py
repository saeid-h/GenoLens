"""Exploratory archaic / Neanderthal-informative SNP affinity."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import SHIPPED_DATA


@dataclass
class ArchaicHit:
    rsid: str
    genotype: str | None
    archaic_allele: str
    carries_archaic: bool
    present: bool
    note: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "rsid": self.rsid,
            "genotype": self.genotype,
            "archaic_allele": self.archaic_allele,
            "carries_archaic": self.carries_archaic,
            "present": self.present,
            "note": self.note,
        }


def load_archaic_panel(path: Path | None = None) -> dict[str, Any]:
    panel_path = path or (SHIPPED_DATA / "archaic_panel.json")
    with panel_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def score_archaic(snps: SNPs, panel: dict[str, Any] | None = None) -> dict[str, Any]:
    panel = panel or load_archaic_panel()
    genotypes = genotype_lookup(snps)
    hits: list[ArchaicHit] = []
    for marker in panel.get("markers", []):
        rsid = marker["rsid"]
        archaic = marker["archaic_allele"]
        geno = genotypes.get(rsid)
        present = geno is not None
        carries = bool(present and archaic.upper() in geno.upper())
        hits.append(
            ArchaicHit(
                rsid=rsid,
                genotype=geno,
                archaic_allele=archaic,
                carries_archaic=carries,
                present=present,
                note=marker.get("note", ""),
            )
        )
    present_n = sum(1 for h in hits if h.present)
    carry_n = sum(1 for h in hits if h.carries_archaic)
    return {
        "disclaimer": panel.get("disclaimer", ""),
        "markers_present": present_n,
        "markers_tested": len(hits),
        "archaic_allele_hits": carry_n,
        "fraction_of_present": (carry_n / present_n) if present_n else 0.0,
        "hits": [h.as_dict() for h in hits],
    }
