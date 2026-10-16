"""Shallow Y / mtDNA haplogroup hints from a bundled marker tree."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import SHIPPED_DATA


@dataclass
class HaplogroupCall:
    lineage: str  # "Y" or "mt"
    haplogroup: str | None
    path: list[str]
    markers_tested: int
    markers_called: int
    note: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "lineage": self.lineage,
            "haplogroup": self.haplogroup,
            "path": self.path,
            "markers_tested": self.markers_tested,
            "markers_called": self.markers_called,
            "note": self.note,
        }


def load_tree(path: Path | None = None) -> dict[str, Any]:
    tree_path = path or (SHIPPED_DATA / "haplogroups.json")
    with tree_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _allele_matches(genotype: str | None, derived: str) -> bool:
    if not genotype or genotype in {"--", "nan"}:
        return False
    # Haploid Y/mt often reported as single letter; diploid may include derived
    return derived.upper() in genotype.upper()


def _call_branch(markers: list[dict[str, Any]], genotypes: dict[str, str]) -> HaplogroupCall:
    lineage_label = "Y"  # overwritten by caller
    tested = len(markers)
    called = 0
    by_name = {m["haplogroup"]: m for m in markers}
    # Walk deepest derived path: start from roots (parent is None) and descend
    path: list[str] = []
    frontier = [m for m in markers if m.get("parent") is None]
    visited: set[str] = set()

    while frontier:
        next_frontier: list[dict[str, Any]] = []
        progressed = False
        for marker in frontier:
            name = marker["haplogroup"]
            if name in visited:
                continue
            visited.add(name)
            geno = genotypes.get(marker["rsid"])
            if geno is not None and geno not in {"--", "nan"}:
                called += 1
            if _allele_matches(geno, marker["derived"]):
                path.append(name)
                progressed = True
                children = [m for m in markers if m.get("parent") == name]
                next_frontier.extend(children)
        if not progressed:
            break
        frontier = next_frontier

    called = sum(1 for m in markers if genotypes.get(m["rsid"]) not in (None, "--", "nan"))
    tip = path[-1] if path else None
    if called == 0:
        note = "No haplogroup markers from this tree were called on this chip."
    elif tip is None:
        note = "Markers present but no derived alleles matched this shallow tree."
    else:
        note = f"Deepest matched branch: {tip}. Consumer chips often cannot resolve finer subclades."

    return HaplogroupCall(
        lineage=lineage_label,
        haplogroup=tip,
        path=path,
        markers_tested=tested,
        markers_called=called,
        note=note,
    )


def call_haplogroups(snps: SNPs, tree: dict[str, Any] | None = None) -> dict[str, HaplogroupCall]:
    tree = tree or load_tree()
    genotypes = genotype_lookup(snps)
    y_call = _call_branch(tree.get("y", []), genotypes)
    y_call.lineage = "Y"
    mt_call = _call_branch(tree.get("mt", []), genotypes)
    mt_call.lineage = "mt"
    return {"Y": y_call, "mt": mt_call}
