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
    evidence: list[dict[str, Any]] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "lineage": self.lineage,
            "haplogroup": self.haplogroup,
            "path": self.path,
            "markers_tested": self.markers_tested,
            "markers_called": self.markers_called,
            "note": self.note,
            "evidence": list(self.evidence or []),
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


def _children_of(markers: list[dict[str, Any]], parent_name: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for marker in markers:
        if marker.get("parent") == parent_name:
            out.append(marker)
        display = _display_name(marker)
        # also allow parent field matching alias display names of other nodes
        if marker.get("parent") and marker.get("parent") != parent_name:
            continue
    # Include children whose parent equals this node's raw or display name
    for marker in markers:
        if marker.get("parent") in {parent_name, parent_name}:
            if marker not in out:
                out.append(marker)
    # Deduplicate by haplogroup key
    seen: set[str] = set()
    uniq: list[dict[str, Any]] = []
    for marker in markers:
        if marker.get("parent") != parent_name:
            continue
        key = marker["haplogroup"]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(marker)
    return uniq


def _best_path(
    marker: dict[str, Any],
    markers: list[dict[str, Any]],
    genotypes: dict[str, str],
    pos_index: dict[tuple[str, int], str],
    evidence: list[dict[str, Any]],
) -> tuple[list[str], int]:
    """Return (path_labels, derived_hit_count) for the best subtree under marker."""
    geno = _marker_genotype(marker, genotypes, pos_index)
    derived_hit = _allele_matches(geno, marker["derived"])
    missing = geno is None
    soft = bool(marker.get("soft_pass") or marker.get("optional_root")) and (
        missing or not derived_hit
    )
    label = _display_name(marker)
    snp_name = marker.get("snp_name") or marker.get("rsid") or marker.get("pos")
    evidence.append(
        {
            "haplogroup": label,
            "snp": snp_name,
            "rsid": marker.get("rsid"),
            "genotype": geno,
            "derived": marker["derived"],
            "match": derived_hit,
            "missing": missing,
            "soft_pass": soft and not derived_hit,
        }
    )

    children = _children_of(markers, marker["haplogroup"])
    # Also children of alias target when this node is an alias source
    if marker.get("alias_of"):
        children = children + [
            m for m in _children_of(markers, marker["alias_of"]) if m not in children
        ]

    child_results: list[tuple[list[str], int]] = []
    for child in children:
        child_results.append(_best_path(child, markers, genotypes, pos_index, evidence))

    best_child_path: list[str] = []
    best_child_hits = 0
    if child_results:
        best_child_path, best_child_hits = max(child_results, key=lambda item: (item[1], len(item[0])))

    if derived_hit:
        path = [label] if not best_child_path or best_child_path[0] != label else []
        if not path:
            path = [label]
        return path + best_child_path, 1 + best_child_hits

    if soft:
        # Do not add this node to the path; only keep downstream derived evidence.
        return best_child_path, best_child_hits

    return [], 0


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

    roots = [m for m in markers if m.get("parent") is None]
    evidence: list[dict[str, Any]] = []
    best_path: list[str] = []
    best_hits = 0
    for root in roots:
        path, hits = _best_path(root, markers, genotypes, pos_index, evidence)
        if hits > best_hits or (hits == best_hits and len(path) > len(best_path)):
            best_path, best_hits = path, hits

    # Deduplicate evidence by haplogroup+rsid keeping last
    uniq_ev: dict[str, dict[str, Any]] = {}
    for row in evidence:
        key = f"{row.get('haplogroup')}:{row.get('rsid')}"
        uniq_ev[key] = row
    evidence_out = list(uniq_ev.values())

    tip = best_path[-1] if best_path else None
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
            "GenoLens uses a small open SNP tree; 23andMe uses thousands of Y markers "
            "(including private i-ids), so their paternal haplogroup is usually much finer."
        )

    return HaplogroupCall(
        lineage="Y",
        haplogroup=tip,
        path=best_path,
        markers_tested=tested,
        markers_called=called,
        note=note,
        evidence=evidence_out,
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
