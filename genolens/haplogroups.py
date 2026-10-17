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
    return derived.upper() in genotype.upper()


def _build_pos_index(snps: SNPs, *, mt_only: bool = True) -> dict[tuple[str, int], str]:
    """Map (chrom, pos) -> genotype for position-based markers (MT by default)."""
    frame = snps.snps
    if frame is None or frame.empty or "genotype" not in frame.columns:
        return {}
    if "chrom" not in frame.columns or "pos" not in frame.columns:
        return {}
    work = frame
    if mt_only:
        chrom_s = work["chrom"].astype(str).str.upper().str.replace("CHR", "", regex=False)
        work = work[chrom_s.isin(["MT", "M", "26"])]
    out: dict[tuple[str, int], str] = {}
    for rsid, row in work.iterrows():
        try:
            chrom = str(row["chrom"]).upper().replace("CHR", "")
            if chrom in {"M", "MT", "26"}:
                chrom = "MT"
            pos = int(row["pos"])
            geno = str(row["genotype"])
            if geno and geno not in {"--", "nan"}:
                out[(chrom, pos)] = geno
        except Exception:  # noqa: BLE001
            continue
    return out


def _marker_genotype(
    marker: dict[str, Any],
    genotypes: dict[str, str],
    pos_index: dict[tuple[str, int], str],
) -> str | None:
    rsid = marker.get("rsid")
    if rsid:
        geno = genotypes.get(rsid)
        if geno not in (None, "--", "nan"):
            return geno
    chrom = marker.get("chrom")
    pos = marker.get("pos")
    if chrom and pos is not None:
        chrom_n = str(chrom).upper().replace("CHR", "")
        if chrom_n in {"M", "26"}:
            chrom_n = "MT"
        return pos_index.get((chrom_n, int(pos)))
    return None


def _display_name(marker: dict[str, Any]) -> str:
    return marker.get("alias_of") or marker["haplogroup"]


def _call_branch(
    markers: list[dict[str, Any]],
    genotypes: dict[str, str],
    pos_index: dict[tuple[str, int], str] | None = None,
) -> HaplogroupCall:
    pos_index = pos_index or {}
    tested = len(markers)
    called = 0
    for marker in markers:
        if _marker_genotype(marker, genotypes, pos_index) is not None:
            called += 1

    # Soft-pass missing optional roots: start from roots, but if a parent SNP is
    # absent on the chip, still evaluate children.
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
            geno = _marker_genotype(marker, genotypes, pos_index)
            derived_hit = _allele_matches(geno, marker["derived"])
            missing = geno is None
            optional = bool(marker.get("optional_root")) or missing

            children = [m for m in markers if m.get("parent") == name]
            # Also accept children whose parent field is the alias target
            display = _display_name(marker)
            children += [
                m
                for m in markers
                if m.get("parent") == display and m not in children
            ]

            if derived_hit:
                label = display
                if not path or path[-1] != label:
                    path.append(label)
                progressed = True
                next_frontier.extend(children)
            elif optional and children:
                # Missing parent SNP: still explore children
                progressed = True
                next_frontier.extend(children)
        if not progressed:
            break
        frontier = next_frontier

    tip = path[-1] if path else None
    if called == 0:
        note = "No haplogroup markers from this tree were called on this chip."
    elif tip is None:
        note = (
            "Markers present but no derived alleles matched this shallow tree "
            "(often ancestral calls at tested sites)."
        )
    else:
        note = (
            f"Deepest matched branch: {tip}. "
            "Consumer chips often cannot resolve finer subclades."
        )

    return HaplogroupCall(
        lineage="Y",
        haplogroup=tip,
        path=path,
        markers_tested=tested,
        markers_called=called,
        note=note,
    )


def call_haplogroups(snps: SNPs, tree: dict[str, Any] | None = None) -> dict[str, HaplogroupCall]:
    tree = tree or load_tree()
    genotypes = genotype_lookup(snps)
    pos_index = _build_pos_index(snps)

    y_call = _call_branch(tree.get("y", []), genotypes, pos_index)
    y_call.lineage = "Y"
    mt_call = _call_branch(tree.get("mt", []), genotypes, pos_index)
    mt_call.lineage = "mt"

    sex = None
    try:
        sex = snps.determine_sex() if hasattr(snps, "determine_sex") else getattr(snps, "sex", None)
    except Exception:  # noqa: BLE001
        sex = getattr(snps, "sex", None)
    if y_call.markers_called == 0 and str(sex).lower() in {"female", "f"}:
        y_call.note = "No Y markers called (expected for female samples)."

    return {"Y": y_call, "mt": mt_call}
