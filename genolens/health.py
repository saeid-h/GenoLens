"""Match genotypes against a curated exploratory health/trait panel."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import SHIPPED_DATA


@dataclass
class HealthHit:
    rsid: str
    gene: str
    category: str
    summary: str
    genotype: str | None
    note: str
    source: str
    present: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "rsid": self.rsid,
            "gene": self.gene,
            "category": self.category,
            "summary": self.summary,
            "genotype": self.genotype,
            "note": self.note,
            "source": self.source,
            "present": self.present,
        }


def load_panel(path: Path | None = None) -> dict[str, Any]:
    panel_path = path or (SHIPPED_DATA / "health_panel.json")
    with panel_path.open(encoding="utf-8") as fh:
        return json.load(fh)


TRAIT_CATEGORIES = frozenset({"trait"})
WELLNESS_CATEGORIES = frozenset({"metabolism", "wellness"})
PHARMA_CATEGORIES = frozenset({"pharmacogenetics"})
HEALTH_CATEGORIES = frozenset({"health", "carrier"})


def match_health(
    snps: SNPs,
    panel: dict[str, Any] | None = None,
    categories: set[str] | frozenset[str] | None = None,
) -> list[HealthHit]:
    """Return panel rows with genotype-specific notes when the SNP is called."""
    panel = panel or load_panel()
    genotypes = genotype_lookup(snps)
    hits: list[HealthHit] = []

    for marker in panel.get("markers", []):
        if categories is not None and marker.get("category") not in categories:
            continue
        rsid = marker["rsid"]
        geno = genotypes.get(rsid)
        notes = marker.get("notes", {})
        if geno is None:
            note = "Not called on this chip / file."
            present = False
        else:
            # Normalize order for diploid calls (AG == GA)
            key = "".join(sorted(geno)) if len(geno) == 2 and geno.isalpha() else geno
            note = notes.get(geno) or notes.get(key) or f"Genotype {geno} (no panel note for this call)."
            # also try reverse diploid
            if note.startswith("Genotype ") and len(geno) == 2:
                note = notes.get(geno[::-1], note)
            present = True

        hits.append(
            HealthHit(
                rsid=rsid,
                gene=marker.get("gene", ""),
                category=marker.get("category", ""),
                summary=marker.get("summary", ""),
                genotype=geno,
                note=note,
                source=marker.get("source", ""),
                present=present,
            )
        )
    return hits
