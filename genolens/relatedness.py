"""Pairwise relatedness using the lineage library."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from lineage import Lineage
from snps import SNPs

# ISOGG-style autosomal shared-cM bands used for pedigree edges.
PARENT_CHILD_CM = 3400.0
SIBLING_CM_MIN = 2200.0
SIBLING_CM_MAX = 3400.0  # exclusive upper bound vs parent/child
CLOSE_RELATIVE_CM = 1300.0

EdgeKind = Literal["parent_child", "sibling", "close_relative", "distant", "unrelated"]


@dataclass
class PairResult:
    sample_a: str
    sample_b: str
    path_a: Path
    path_b: Path
    shared_cm: float
    shared_segments: int
    relationship: str | None
    segments: pd.DataFrame = field(default_factory=pd.DataFrame)
    chrom_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "sample_a": self.sample_a,
            "sample_b": self.sample_b,
            "shared_cm": self.shared_cm,
            "shared_segments": self.shared_segments,
            "relationship": self.relationship,
            "error": self.error,
        }


@dataclass
class PedigreeEdge:
    """Directed or undirected pedigree link with evidence."""

    source: str  # parent for parent→child; either end for sibling
    target: str
    kind: EdgeKind
    shared_cm: float
    relationship: str
    directed: bool = False  # True when source is inferred parent of target
    confidence: str = "high"  # high | medium | low
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "shared_cm": self.shared_cm,
            "relationship": self.relationship,
            "directed": self.directed,
            "confidence": self.confidence,
            "note": self.note,
        }


@dataclass
class PedigreeNode:
    label: str
    generation: int
    role: str  # e.g. Mother, Father, Parent A, Child, Sibling, Unplaced
    sex: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "generation": self.generation,
            "role": self.role,
            "sex": self.sex,
        }


@dataclass
class PedigreeEstimate:
    nodes: list[PedigreeNode]
    edges: list[PedigreeEdge]
    notes: list[str] = field(default_factory=list)
    ascii_tree: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.as_dict() for n in self.nodes],
            "edges": [e.as_dict() for e in self.edges],
            "notes": list(self.notes),
            "ascii_tree": self.ascii_tree,
        }


def _label(path: Path) -> str:
    from genolens.paths import sample_label

    return sample_label(path)


_CM_COLS = ("cMs", "cM", "cm", "genetic_distance")
_SEG_KEYS = (
    "one_chrom_shared_dna",
    "two_chrom_shared_dna",
    "segments",
    "shared_dna",
)


def _cm_column(frame: pd.DataFrame) -> str | None:
    return next((c for c in _CM_COLS if c in frame.columns), None)


def _extract_segments(result: Any) -> pd.DataFrame:
    """Pull shared-segment tables from a lineage.find_shared_dna result."""
    if result is None:
        return pd.DataFrame()
    if isinstance(result, pd.DataFrame):
        return result.copy()
    if not isinstance(result, dict):
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []
    for key in _SEG_KEYS:
        value = result.get(key)
        if isinstance(value, pd.DataFrame) and not value.empty:
            part = value.copy()
            if "share_type" not in part.columns:
                if key.startswith("two_chrom"):
                    part["share_type"] = "two_chrom"
                elif key.startswith("one_chrom"):
                    part["share_type"] = "one_chrom"
            frames.append(part)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _extract_shared_cm(result: Any, segments: pd.DataFrame | None = None) -> float:
    """Total shared cM. Prefer one-chrom (HIR) total; fall back to segment sum."""
    if isinstance(result, dict):
        for key in ("cM_total", "cm_total", "shared_cm", "total_cm"):
            if key in result and result[key] is not None:
                return float(result[key])
        # lineage 4.x: one_chrom_shared_dna / two_chrom_shared_dna with column `cMs`
        one = result.get("one_chrom_shared_dna")
        if isinstance(one, pd.DataFrame) and not one.empty:
            col = _cm_column(one)
            if col:
                return float(one[col].sum())
        two = result.get("two_chrom_shared_dna")
        if isinstance(two, pd.DataFrame) and not two.empty:
            col = _cm_column(two)
            if col:
                return float(two[col].sum())

    segs = segments if segments is not None else _extract_segments(result)
    if isinstance(segs, pd.DataFrame) and not segs.empty:
        # Prefer one_chrom rows when both share types are present (avoid double-count).
        if "share_type" in segs.columns and (segs["share_type"] == "one_chrom").any():
            segs = segs[segs["share_type"] == "one_chrom"]
        col = _cm_column(segs)
        if col:
            return float(segs[col].sum())
    return 0.0


def _chrom_summary(segments: pd.DataFrame) -> pd.DataFrame:
    if segments is None or segments.empty:
        return pd.DataFrame(columns=["chrom", "segments", "cM"])
    chrom_col = next((c for c in ("chrom", "chromosome", "chr") if c in segments.columns), None)
    cm_col = _cm_column(segments)
    if chrom_col is None:
        return pd.DataFrame(columns=["chrom", "segments", "cM"])
    # Summarize HIR segments when typed.
    frame = segments
    if "share_type" in frame.columns and (frame["share_type"] == "one_chrom").any():
        frame = frame[frame["share_type"] == "one_chrom"]
    grouped = frame.groupby(chrom_col, dropna=False)
    rows = []
    for chrom, part in grouped:
        rows.append(
            {
                "chrom": chrom,
                "segments": len(part),
                "cM": float(part[cm_col].sum()) if cm_col else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values("chrom").reset_index(drop=True)


def _relationship_from_cm(shared_cm: float) -> str:
    """Rough relationship band from total shared cM (ISOGG-style ranges)."""
    if shared_cm >= 3400:
        return "Parent/child or identical twin (approx.)"
    if shared_cm >= 2200:
        return "Full sibling (approx.)"
    if shared_cm >= 1300:
        return "Grandparent / aunt-uncle / half-sibling range (approx.)"
    if shared_cm >= 600:
        return "1st cousin / great-grandparent range (approx.)"
    if shared_cm >= 200:
        return "2nd cousin range (approx.)"
    if shared_cm >= 90:
        return "3rd cousin range (approx.)"
    if shared_cm >= 20:
        return "Distant cousin / possible IBD noise (approx.)"
    if shared_cm > 0:
        return "Very little shared DNA"
    return "No shared segments detected"


def compare_pair(
    path_a: str | Path,
    path_b: str | Path,
    snps_a: SNPs | None = None,
    snps_b: SNPs | None = None,
) -> PairResult:
    """Compare two genome files and return shared-segment stats."""
    path_a = Path(path_a)
    path_b = Path(path_b)
    label_a = _label(path_a)
    label_b = _label(path_b)

    try:
        s1 = snps_a or SNPs(str(path_a))
        s2 = snps_b or SNPs(str(path_b))
        # lineage's save path calls Individual.get_var_name(); raw SNPs lack it.
        # Keep computation in-memory.
        lin = Lineage(output_dir=None)
        result = lin.find_shared_dna([s1, s2], save_output=False)
        segments = _extract_segments(result)
        shared_cm = _extract_shared_cm(result, segments)
        rel = None
        if isinstance(result, dict):
            rel = result.get("relationship") or result.get("predicted_relationship")
        if not rel:
            rel = _relationship_from_cm(shared_cm)
        # Count HIR segments for the headline metric when typed.
        if not segments.empty and "share_type" in segments.columns:
            n_segs = int((segments["share_type"] == "one_chrom").sum()) or len(segments)
        else:
            n_segs = int(len(segments)) if segments is not None else 0
        return PairResult(
            sample_a=label_a,
            sample_b=label_b,
            path_a=path_a,
            path_b=path_b,
            shared_cm=float(shared_cm),
            shared_segments=n_segs,
            relationship=str(rel) if rel else None,
            segments=segments if segments is not None else pd.DataFrame(),
            chrom_summary=_chrom_summary(segments),
        )
    except Exception as exc:  # noqa: BLE001 — surface to UI
        return PairResult(
            sample_a=label_a,
            sample_b=label_b,
            path_a=path_a,
            path_b=path_b,
            shared_cm=0.0,
            shared_segments=0,
            relationship=None,
            error=str(exc),
        )


def compare_all_pairs(paths: list[Path]) -> list[PairResult]:
    """Compare every unordered pair among ``paths``."""
    results: list[PairResult] = []
    for a, b in combinations(paths, 2):
        results.append(compare_pair(a, b))
    return results


def relatedness_matrix_from_pairs(pairs: list[PairResult], labels: list[str]) -> pd.DataFrame:
    """Build a symmetric shared-cM matrix from precomputed pair results."""
    frame = pd.DataFrame(float("nan"), index=labels, columns=labels)
    by_pair = {_pair_key(p.sample_a, p.sample_b): p for p in pairs}
    for a, b in combinations(labels, 2):
        pair = by_pair.get(_pair_key(a, b))
        cm = float("nan")
        if pair is not None and pair.error is None:
            cm = float(pair.shared_cm)
        frame.loc[a, b] = cm
        frame.loc[b, a] = cm
    return frame


def relatedness_matrix(paths: list[Path]) -> pd.DataFrame:
    """Symmetric matrix of shared cM across samples."""
    labels = [_label(p) for p in paths]
    return relatedness_matrix_from_pairs(compare_all_pairs(paths), labels)


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def _edge_kind(shared_cm: float) -> EdgeKind:
    if shared_cm >= PARENT_CHILD_CM:
        return "parent_child"
    if shared_cm >= SIBLING_CM_MIN:
        return "sibling"
    if shared_cm >= CLOSE_RELATIVE_CM:
        return "close_relative"
    if shared_cm > 0:
        return "distant"
    return "unrelated"


def _norm_sex(sex: str | None) -> str | None:
    if not sex:
        return None
    s = str(sex).strip().lower()
    if s in {"m", "male"}:
        return "male"
    if s in {"f", "female"}:
        return "female"
    return None


_PARENT_ROLES = frozenset({"Mother", "Father", "Parent", "Parent A", "Parent B"})


def _is_parent_role(role: str | None) -> bool:
    return role in _PARENT_ROLES


def _cm_lookup(pairs: list[PairResult]) -> dict[tuple[str, str], PairResult]:
    return {_pair_key(p.sample_a, p.sample_b): p for p in pairs if p.error is None}


def _parent_role_labels(parents: list[str], sex_by_label: dict[str, str | None]) -> dict[str, str]:
    """Assign Mother/Father or Parent A/B for up to two parents of a sibling set."""
    roles: dict[str, str] = {}
    if len(parents) == 1:
        sex = _norm_sex(sex_by_label.get(parents[0]))
        if sex == "female":
            roles[parents[0]] = "Mother"
        elif sex == "male":
            roles[parents[0]] = "Father"
        else:
            roles[parents[0]] = "Parent"
        return roles

    if len(parents) >= 2:
        # Prefer sex-based Mother/Father when both known and opposite.
        sexes = {p: _norm_sex(sex_by_label.get(p)) for p in parents[:2]}
        female = [p for p, s in sexes.items() if s == "female"]
        male = [p for p, s in sexes.items() if s == "male"]
        if len(female) == 1 and len(male) == 1:
            roles[female[0]] = "Mother"
            roles[male[0]] = "Father"
            for p in parents[2:]:
                roles[p] = "Parent (ambiguous)"
            return roles
        # Sex unknown or same-sex / incomplete → Parent A/B (do not invent genders).
        for i, p in enumerate(parents):
            if i == 0:
                roles[p] = "Parent A"
            elif i == 1:
                roles[p] = "Parent B"
            else:
                roles[p] = "Parent (ambiguous)"
        return roles
    return roles


def infer_pedigree(
    pairs: list[PairResult],
    sex_by_label: dict[str, str | None] | None = None,
    labels: list[str] | None = None,
) -> PedigreeEstimate:
    """Best-effort nuclear pedigree from pairwise shared-cM bands.

    Practical algorithm for small local cohorts (e.g. 2–6 samples):

    1. Classify pairs: parent/child (≥3400 cM), sibling (2200–3400), else weaker.
    2. Autosomal parent/child cM is symmetric — orient edges using sibling structure:
       someone parent/child to two+ mutual siblings is the parent generation.
    3. Two adults both parent/child to the same child(ren) and ~unrelated to each
       other are treated as co-parents (Mother/Father when SNP-derived sex is known).
    4. Ambiguous graphs stay undirected / low-confidence with notes — never invent
       impossible multi-parent cycles.
    """
    sex_by_label = dict(sex_by_label or {})
    lookup = _cm_lookup(pairs)
    if labels is None:
        labels = sorted({p.sample_a for p in pairs} | {p.sample_b for p in pairs})
    notes: list[str] = []

    pc_pairs: list[tuple[str, str, PairResult]] = []
    sib_pairs: list[tuple[str, str, PairResult]] = []
    other_edges: list[PedigreeEdge] = []

    for key, pair in lookup.items():
        a, b = key
        kind = _edge_kind(pair.shared_cm)
        rel = pair.relationship or _relationship_from_cm(pair.shared_cm)
        if kind == "parent_child":
            pc_pairs.append((a, b, pair))
        elif kind == "sibling":
            sib_pairs.append((a, b, pair))
        elif kind in {"close_relative", "distant"}:
            other_edges.append(
                PedigreeEdge(
                    source=a,
                    target=b,
                    kind=kind,
                    shared_cm=pair.shared_cm,
                    relationship=rel,
                    directed=False,
                    confidence="low" if kind == "distant" else "medium",
                    note="Not used for nuclear tree placement.",
                )
            )

    # Union-find sibling clusters from sibling-band edges.
    parent_of: dict[str, str] = {lab: lab for lab in labels}

    def find(x: str) -> str:
        while parent_of[x] != x:
            parent_of[x] = parent_of[parent_of[x]]
            x = parent_of[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent_of[rb] = ra

    for a, b, _ in sib_pairs:
        union(a, b)

    clusters: dict[str, list[str]] = {}
    for lab in labels:
        clusters.setdefault(find(lab), []).append(lab)

    directed: list[PedigreeEdge] = []
    generation: dict[str, int] = {lab: 0 for lab in labels}
    roles: dict[str, str] = {lab: "Unplaced" for lab in labels}
    placed_pc: set[tuple[str, str]] = set()

    def _outsider_hits(members: list[str]) -> dict[str, list[str]]:
        hits: dict[str, list[str]] = {}
        member_set = set(members)
        for a, b, _pair in pc_pairs:
            if a in member_set and b not in member_set:
                hits.setdefault(b, []).append(a)
            elif b in member_set and a not in member_set:
                hits.setdefault(a, []).append(b)
            elif a in member_set and b in member_set:
                notes.append(
                    f"{a}–{b}: parent/child-range cM but both sit in the same sibling "
                    f"cluster — treating as ambiguous (identical twin / mis-band)."
                )
        return hits

    def _choose_parents(
        members: list[str], outsider_hits: dict[str, list[str]]
    ) -> list[str]:
        ranked = sorted(
            outsider_hits.items(),
            key=lambda item: (
                -len(item[1]),
                -max(
                    lookup[_pair_key(item[0], m)].shared_cm
                    for m in item[1]
                    if _pair_key(item[0], m) in lookup
                ),
            ),
        )
        chosen: list[str] = []
        for cand, kids in ranked:
            if len(chosen) >= 2:
                break
            # Skip people already placed as children (prevents inverting PC edges).
            if roles.get(cand) == "Child":
                continue
            if any(_is_parent_role(roles.get(k)) for k in kids):
                continue
            conflict = False
            for other in chosen:
                pk = _pair_key(cand, other)
                if pk in lookup and _edge_kind(lookup[pk].shared_cm) in {"parent_child", "sibling"}:
                    notes.append(
                        f"Skipped {cand} as co-parent with {other}: pair looks "
                        f"{_edge_kind(lookup[pk].shared_cm)} ({lookup[pk].shared_cm:.0f} cM)."
                    )
                    conflict = True
                    break
            if not conflict:
                chosen.append(cand)
        return chosen

    def _assign_parents_to_cluster(members: list[str], chosen_parents: list[str], outsider_hits: dict[str, list[str]]) -> None:
        parent_roles = _parent_role_labels(chosen_parents, sex_by_label)
        for p in chosen_parents:
            roles[p] = parent_roles.get(p, "Parent")
            generation[p] = 0
            linked = [c for c in outsider_hits.get(p, []) if c in members]
            missing = [m for m in members if m not in linked]
            if missing and len(members) >= 2:
                notes.append(
                    f"{p} is parent/child-range to {', '.join(linked)} but not to "
                    f"{', '.join(missing)} — possible half-sibling / step configuration; "
                    f"do not invent missing parents."
                )
            for child in linked:
                pair = lookup[_pair_key(p, child)]
                conf = "high" if len(linked) >= min(2, max(1, len(members))) else "medium"
                if missing:
                    conf = "medium"
                directed.append(
                    PedigreeEdge(
                        source=p,
                        target=child,
                        kind="parent_child",
                        shared_cm=pair.shared_cm,
                        relationship=pair.relationship or _relationship_from_cm(pair.shared_cm),
                        directed=True,
                        confidence=conf,
                        note=f"Inferred {roles[p]} → child.",
                    )
                )
                placed_pc.add(_pair_key(p, child))
                roles[child] = "Child"
                generation[child] = 1
        if any(roles[m] == "Child" for m in members):
            for m in members:
                if roles[m] == "Unplaced":
                    roles[m] = "Child"
                    generation[m] = 1

    # Pass 1: sibling groups (size ≥ 2) — strongest orientation signal.
    multi = sorted(
        (sorted(m) for m in clusters.values() if len(m) >= 2),
        key=lambda m: -len(m),
    )
    for members in multi:
        hits = _outsider_hits(members)
        chosen = _choose_parents(members, hits)
        if chosen:
            _assign_parents_to_cluster(members, chosen, hits)
        else:
            for m in members:
                if roles[m] == "Unplaced":
                    roles[m] = "Sibling"
                    generation[m] = 1

    # Pass 2: single-child nuclear families — two PC outsiders who are not
    # close relatives of each other, and neither is already a Child.
    singles = sorted(m[0] for m in clusters.values() if len(m) == 1)
    for child in singles:
        if roles[child] != "Unplaced":
            continue
        hits = _outsider_hits([child])
        # Need two co-parent candidates (or one if only one PC link exists).
        candidates = [
            c for c in hits if roles.get(c) != "Child" and not _is_parent_role(roles.get(c))
        ]
        if len(candidates) >= 2:
            chosen = _choose_parents([child], {c: hits[c] for c in candidates})
            if len(chosen) >= 2:
                _assign_parents_to_cluster([child], chosen[:2], hits)
        elif len(candidates) == 1 and len(hits) == 1:
            # Lone parent/child pair with no sibling context — leave undirected later.
            pass

    # Sibling edges among children / sibling-band pairs.
    for a, b, pair in sib_pairs:
        directed.append(
            PedigreeEdge(
                source=a,
                target=b,
                kind="sibling",
                shared_cm=pair.shared_cm,
                relationship=pair.relationship or _relationship_from_cm(pair.shared_cm),
                directed=False,
                confidence="high",
                note="Sibling-range shared cM.",
            )
        )
        for lab in (a, b):
            if roles[lab] == "Unplaced":
                roles[lab] = "Sibling"
                generation[lab] = max(generation.get(lab, 0), 1)

    # Orient leftover PC edges when one end is already a known parent or child.
    for a, b, pair in pc_pairs:
        key = _pair_key(a, b)
        if key in placed_pc:
            continue
        if _is_parent_role(roles.get(a)) and roles.get(b) in {"Child", "Sibling", "Unplaced"}:
            src, tgt = a, b
        elif _is_parent_role(roles.get(b)) and roles.get(a) in {"Child", "Sibling", "Unplaced"}:
            src, tgt = b, a
        else:
            directed.append(
                PedigreeEdge(
                    source=a,
                    target=b,
                    kind="parent_child",
                    shared_cm=pair.shared_cm,
                    relationship=pair.relationship or _relationship_from_cm(pair.shared_cm),
                    directed=False,
                    confidence="low",
                    note="Parent/child-range cM; generation orientation ambiguous.",
                )
            )
            notes.append(f"{a}–{b}: parent/child band without clear parent orientation.")
            continue
        directed.append(
            PedigreeEdge(
                source=src,
                target=tgt,
                kind="parent_child",
                shared_cm=pair.shared_cm,
                relationship=pair.relationship or _relationship_from_cm(pair.shared_cm),
                directed=True,
                confidence="medium",
                note=f"Oriented using existing roles ({roles.get(src)} → child).",
            )
        )
        placed_pc.add(key)
        roles[tgt] = "Child"
        generation[tgt] = max(generation.get(tgt, 0), generation.get(src, 0) + 1)

    directed.extend(other_edges)

    # Normalize generations so the top generation is 0.
    if any(roles[lab] != "Unplaced" for lab in labels):
        min_gen = min(generation[lab] for lab in labels if roles[lab] != "Unplaced")
        for lab in labels:
            if roles[lab] != "Unplaced":
                generation[lab] -= min_gen

    nodes = [
        PedigreeNode(
            label=lab,
            generation=generation[lab],
            role=roles[lab],
            sex=_norm_sex(sex_by_label.get(lab)),
        )
        for lab in sorted(labels, key=lambda x: (generation[x], roles[x], x))
    ]
    if not any(e.kind in {"parent_child", "sibling"} for e in directed):
        notes.append("No parent/child or sibling-range pairs — cannot sketch a nuclear tree.")

    ascii_tree = format_pedigree_ascii(nodes, directed)
    return PedigreeEstimate(nodes=nodes, edges=directed, notes=notes, ascii_tree=ascii_tree)


def format_pedigree_ascii(nodes: list[PedigreeNode], edges: list[PedigreeEdge]) -> str:
    """Simple parents-above-children ASCII sketch."""
    if not nodes:
        return "(empty)"
    by_gen: dict[int, list[PedigreeNode]] = {}
    for n in nodes:
        by_gen.setdefault(n.generation, []).append(n)

    parent_child = [e for e in edges if e.kind == "parent_child" and e.directed]
    sibling = [e for e in edges if e.kind == "sibling"]

    lines: list[str] = []
    gens = sorted(by_gen)
    for gi, g in enumerate(gens):
        labels = [f"{n.label} [{n.role}]" for n in by_gen[g]]
        lines.append("    ".join(labels))
        if gi < len(gens) - 1:
            # connectors from this gen to next
            links = []
            for e in parent_child:
                if any(n.label == e.source for n in by_gen[g]) and any(
                    n.label == e.target for n in by_gen.get(gens[gi + 1], [])
                ):
                    links.append(f"{e.source}──({e.shared_cm:.0f} cM)──▶{e.target}")
            if links:
                lines.append("  " + "  ".join(links))
            else:
                lines.append("           │")
    if sibling:
        sib_bits = [
            f"{e.source} ↔ {e.target} ({e.shared_cm:.0f} cM, sibling)"
            for e in sibling
        ]
        lines.append("Siblings: " + "; ".join(sib_bits))
    return "\n".join(lines)


def pedigree_plotly_figure(estimate: PedigreeEstimate):
    """Build a Plotly figure: parents above children, edges labeled with cM."""
    import plotly.graph_objects as go

    nodes = estimate.nodes
    if not nodes:
        fig = go.Figure()
        fig.update_layout(title="No samples for pedigree")
        return fig

    # Layout: generation on y (parents high), spread on x within generation.
    by_gen: dict[int, list[PedigreeNode]] = {}
    for n in nodes:
        by_gen.setdefault(n.generation, []).append(n)
    pos: dict[str, tuple[float, float]] = {}
    max_gen = max(by_gen) if by_gen else 0
    for g, members in by_gen.items():
        members = sorted(members, key=lambda n: n.label)
        y = float(max_gen - g)
        for i, n in enumerate(members):
            x = i - (len(members) - 1) / 2.0
            pos[n.label] = (x, y)

    edge_traces = []
    annotations = []
    for e in estimate.edges:
        if e.source not in pos or e.target not in pos:
            continue
        if e.kind not in {"parent_child", "sibling"}:
            continue
        x0, y0 = pos[e.source]
        x1, y1 = pos[e.target]
        color = "#2a6f97" if e.kind == "parent_child" else "#8a5a44"
        dash = "solid" if e.directed or e.kind == "sibling" else "dot"
        edge_traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=color, width=2, dash=dash),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        label = f"{e.shared_cm:.0f} cM"
        if e.kind == "sibling":
            label = f"sib · {label}"
        elif e.directed:
            label = f"p/c · {label}"
        else:
            label = f"p/c? · {label}"
        annotations.append(
            dict(
                x=mx,
                y=my,
                text=label,
                showarrow=False,
                font=dict(size=11, color="#333"),
                bgcolor="rgba(255,255,255,0.75)",
            )
        )

    xs = [pos[n.label][0] for n in nodes]
    ys = [pos[n.label][1] for n in nodes]
    texts = [f"{n.label}<br>{n.role}" + (f" · {n.sex}" if n.sex else "") for n in nodes]
    node_trace = go.Scatter(
        x=xs,
        y=ys,
        mode="markers+text",
        text=[n.label for n in nodes],
        textposition="top center",
        marker=dict(size=28, color="#e8f1f5", line=dict(color="#1b3a4b", width=2)),
        hovertext=texts,
        hoverinfo="text",
        showlegend=False,
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title="Estimated family tree (best-effort from shared cM)",
        annotations=annotations,
        xaxis=dict(visible=False, range=[(min(xs) if xs else 0) - 1.2, (max(xs) if xs else 0) + 1.2]),
        yaxis=dict(visible=False, range=[(min(ys) if ys else 0) - 0.6, (max(ys) if ys else 0) + 0.8]),
        margin=dict(l=20, r=20, t=50, b=20),
        height=420,
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
