"""Pairwise relatedness using the lineage library."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd
from lineage import Lineage
from snps import SNPs


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


def _label(path: Path) -> str:
    from genolens.paths import sample_label

    return sample_label(path)


def _extract_shared_cm(result: Any) -> float:
    if result is None:
        return 0.0
    if isinstance(result, dict):
        for key in ("cM_total", "cm_total", "shared_cm", "total_cm"):
            if key in result and result[key] is not None:
                return float(result[key])
        segs = result.get("segments")
        if isinstance(segs, pd.DataFrame) and not segs.empty:
            for col in ("cM", "cm", "genetic_distance"):
                if col in segs.columns:
                    return float(segs[col].sum())
    if isinstance(result, pd.DataFrame) and not result.empty:
        for col in ("cM", "cm", "genetic_distance"):
            if col in result.columns:
                return float(result[col].sum())
    return 0.0


def _extract_segments(result: Any) -> pd.DataFrame:
    if result is None:
        return pd.DataFrame()
    if isinstance(result, pd.DataFrame):
        return result.copy()
    if isinstance(result, dict):
        segs = result.get("segments")
        if isinstance(segs, pd.DataFrame):
            return segs.copy()
    return pd.DataFrame()


def _chrom_summary(segments: pd.DataFrame) -> pd.DataFrame:
    if segments is None or segments.empty:
        return pd.DataFrame(columns=["chrom", "segments", "cM"])
    chrom_col = next((c for c in ("chrom", "chromosome", "chr") if c in segments.columns), None)
    cm_col = next((c for c in ("cM", "cm", "genetic_distance") if c in segments.columns), None)
    if chrom_col is None:
        return pd.DataFrame(columns=["chrom", "segments", "cM"])
    grouped = segments.groupby(chrom_col, dropna=False)
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
        lin = Lineage(output_dir=None)
        # lineage.find_shared_dna expects SNPs objects
        result = lin.find_shared_dna([s1, s2])
        segments = _extract_segments(result)
        shared_cm = _extract_shared_cm(result)
        if shared_cm == 0.0 and not segments.empty:
            shared_cm = _extract_shared_cm(segments)
        rel = None
        if isinstance(result, dict):
            rel = result.get("relationship") or result.get("predicted_relationship")
        if not rel:
            rel = _relationship_from_cm(shared_cm)
        return PairResult(
            sample_a=label_a,
            sample_b=label_b,
            path_a=path_a,
            path_b=path_b,
            shared_cm=float(shared_cm),
            shared_segments=int(len(segments)) if segments is not None else 0,
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


def relatedness_matrix(paths: list[Path]) -> pd.DataFrame:
    """Symmetric matrix of shared cM across samples."""
    labels = [_label(p) for p in paths]
    frame = pd.DataFrame(0.0, index=labels, columns=labels)
    for i, p in enumerate(paths):
        frame.iloc[i, i] = float("nan")
    for a, b in combinations(range(len(paths)), 2):
        pair = compare_pair(paths[a], paths[b])
        cm = pair.shared_cm if pair.error is None else float("nan")
        frame.iloc[a, b] = cm
        frame.iloc[b, a] = cm
    return frame
