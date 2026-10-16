"""Ancient DNA affinity: allele-sharing distance + PCA projection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import SHIPPED_DATA
from genolens.reference import ensure_panel, load_panel, panel_ready


@dataclass
class AncientMatch:
    genetic_id: str
    group: str
    country: str
    date: Any
    distance: float
    n_snps: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "genetic_id": self.genetic_id,
            "group": self.group,
            "country": self.country,
            "date": self.date,
            "distance": self.distance,
            "n_snps": self.n_snps,
        }


def load_named_remains(path: Path | None = None) -> dict[str, Any]:
    p = path or (SHIPPED_DATA / "named_remains.json")
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def _user_dosage(snps: SNPs, snp_ids: np.ndarray, refs: np.ndarray, alts: np.ndarray) -> np.ndarray:
    """Map user genotypes to alt-allele dosage 0/1/2; 9 = missing/unusable."""
    genotypes = genotype_lookup(snps)
    out = np.full(len(snp_ids), 9, dtype=np.uint8)
    for i, rsid in enumerate(snp_ids):
        geno = genotypes.get(str(rsid))
        if not geno or geno in {"--", "nan"}:
            continue
        ref = str(refs[i]).upper()
        alt = str(alts[i]).upper()
        alleles = [a.upper() for a in geno if a.upper() in "ACGT"]
        if not alleles:
            continue
        # count alt alleles
        alt_count = sum(1 for a in alleles if a == alt)
        ref_count = sum(1 for a in alleles if a == ref)
        if alt_count + ref_count == 0:
            continue
        # diploid expectation; haploid → 0 or 2
        if len(alleles) == 1:
            out[i] = 2 if alleles[0] == alt else 0
        else:
            out[i] = min(2, alt_count)
    return out


def allele_sharing_distance(user: np.ndarray, panel: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mean absolute dosage difference on sites called in both; return (dist, n_snps)."""
    n_samples = panel.shape[1]
    dists = np.full(n_samples, np.nan)
    counts = np.zeros(n_samples, dtype=int)
    user_ok = user != 9
    for j in range(n_samples):
        both = user_ok & (panel[:, j] != 9)
        n = int(both.sum())
        counts[j] = n
        if n < 10:
            continue
        dists[j] = float(np.mean(np.abs(user[both].astype(float) - panel[both, j].astype(float))))
    return dists, counts


def rank_matches(
    snps: SNPs,
    panel_base: Path | None = None,
    top_k: int = 25,
    min_snps: int = 20,
) -> dict[str, Any]:
    ensure_panel(panel_base, use_demo_if_missing=True)
    panel = load_panel(panel_base)
    user = _user_dosage(snps, panel["snp_ids"], panel["refs"], panel["alts"])
    dists, counts = allele_sharing_distance(user, panel["genotypes"])
    ann = panel["annotation"].copy()
    ann["distance"] = dists
    ann["n_snps"] = counts
    usable = ann[ann["n_snps"] >= min_snps].dropna(subset=["distance"]).sort_values("distance")
    individuals = [
        AncientMatch(
            genetic_id=str(row.get("genetic_id", "")),
            group=str(row.get("group", "")),
            country=str(row.get("country", "")),
            date=row.get("date", ""),
            distance=float(row["distance"]),
            n_snps=int(row["n_snps"]),
        )
        for _, row in usable.head(top_k).iterrows()
    ]

    # Population / group summary (empty when no overlapping SNPs / usable samples)
    group_cols = ["group", "mean_distance", "n_individuals", "median_n_snps"]
    group_rows = []
    if not usable.empty and "group" in usable.columns:
        for group, part in usable.groupby("group"):
            group_rows.append(
                {
                    "group": group,
                    "mean_distance": float(part["distance"].mean()),
                    "n_individuals": int(len(part)),
                    "median_n_snps": float(part["n_snps"].median()),
                }
            )
    groups = (
        pd.DataFrame(group_rows, columns=group_cols)
        .sort_values("mean_distance")
        .reset_index(drop=True)
        if group_rows
        else pd.DataFrame(columns=group_cols)
    )

    return {
        "individuals": individuals,
        "groups": groups,
        "meta": panel.get("meta", {}),
        "user_called_snps": int((user != 9).sum()),
        "panel_snps": int(len(panel["snp_ids"])),
        "is_demo": panel.get("meta", {}).get("source") == "synthetic_demo",
    }


def project_pca(
    snps: SNPs,
    panel_base: Path | None = None,
    n_components: int = 2,
) -> dict[str, Any]:
    """Fit PCA on reference samples only, then project the user (lsqproject-style)."""
    ensure_panel(panel_base, use_demo_if_missing=True)
    panel = load_panel(panel_base)
    geno = panel["genotypes"].astype(float)
    geno[geno == 9] = np.nan
    # Impute reference missing with column means for PCA fit
    col_means = np.nanmean(geno, axis=0)
    inds = np.where(np.isnan(geno))
    geno[inds] = np.take(col_means, inds[1])

    # Transpose: samples x SNPs
    X = geno.T
    pca = PCA(n_components=n_components, random_state=0)
    coords = pca.fit_transform(X)

    user = _user_dosage(snps, panel["snp_ids"], panel["refs"], panel["alts"]).astype(float)
    user[user == 9] = np.nan
    # Impute user missing with SNP means from reference (row means of geno)
    snp_means = np.nanmean(geno, axis=1)
    miss = np.isnan(user)
    user[miss] = snp_means[miss]
    user_coord = pca.transform(user.reshape(1, -1))[0]

    ann = panel["annotation"].copy()
    ann["PC1"] = coords[:, 0]
    ann["PC2"] = coords[:, 1] if n_components > 1 else 0.0

    return {
        "annotation": ann,
        "user": {"PC1": float(user_coord[0]), "PC2": float(user_coord[1]) if n_components > 1 else 0.0},
        "explained_variance": [float(v) for v in pca.explained_variance_ratio_],
        "meta": panel.get("meta", {}),
        "is_demo": panel.get("meta", {}).get("source") == "synthetic_demo",
    }


def highlight_named(matches: list[AncientMatch], named: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    named = named or load_named_remains()
    hits = []
    id_set = {m.genetic_id.lower() for m in matches}
    group_set = {m.group.lower() for m in matches}
    for person in named.get("individuals", []):
        aliases = [str(a).lower() for a in person.get("aadr_ids", [])]
        found = any(a in id_set or any(a in g for g in group_set) for a in aliases)
        # also substring match genetic_id
        found = found or any(
            any(a in m.genetic_id.lower() or a in m.group.lower() for a in aliases) for m in matches
        )
        hits.append(
            {
                "name": person["name"],
                "notes": person.get("notes", ""),
                "in_top_matches": found,
            }
        )
    return hits


def ancient_status(panel_base: Path | None = None) -> dict[str, Any]:
    ready = panel_ready(panel_base)
    named = load_named_remains()
    return {
        "panel_ready": ready,
        "missing_royals": named.get("missing_royals", []),
        "disclaimer": named.get("disclaimer", ""),
    }
