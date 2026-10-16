"""Broad ancestry prediction via optional ezancestry, with a local AIM fallback."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from snps import SNPs

from genolens.ingest import genotype_lookup
from genolens.paths import SHIPPED_DATA

_EPS = 1e-4

# 1000 Genomes Phase 3 superpopulation codes → plain-language names.
SUPERPOPULATION_LABELS: dict[str, str] = {
    "AFR": "African",
    "AMR": "Admixed American",
    "EAS": "East Asian",
    "EUR": "European",
    "SAS": "South Asian",
}

AIM_METHOD_SUMMARY = (
    "Percentages show broad continental / superpopulation affinity from ancestry-informative "
    "markers (AIMs), not a country, ethnicity, or tribal identity. Values are normalized "
    "likelihood weights that sum to ~100% across superpopulations."
)


def superpopulation_label(code: str | None, labels: dict[str, str] | None = None) -> str:
    """Return ``Full name (CODE)`` for a superpopulation code, or the raw code if unknown."""
    if not code:
        return ""
    key = str(code).upper()
    mapping = labels or SUPERPOPULATION_LABELS
    name = mapping.get(key) or mapping.get(code) or SUPERPOPULATION_LABELS.get(key)
    if name:
        return f"{name} ({key})"
    return str(code)


def normalize_population_weights(populations: dict[str, float]) -> dict[str, float]:
    """Normalize raw scores / likelihood weights so they sum to 1.0."""
    if not populations:
        return {}
    cleaned = {str(k): float(v) for k, v in populations.items() if _is_number(v) and float(v) >= 0}
    total = sum(cleaned.values())
    if total <= 0:
        return {k: 0.0 for k in cleaned}
    return {k: v / total for k, v in cleaned.items()}


def population_percentages(populations: dict[str, float]) -> dict[str, float]:
    """Return percentages (0–100) that sum to ~100 across superpopulations."""
    return {k: v * 100.0 for k, v in normalize_population_weights(populations).items()}


def _panel_labels(panel: dict[str, Any] | None = None) -> dict[str, str]:
    panel = panel or _load_aim_panel()
    merged = dict(SUPERPOPULATION_LABELS)
    raw = panel.get("labels") or {}
    if isinstance(raw, dict):
        merged.update({str(k).upper(): str(v) for k, v in raw.items()})
    return merged


def _method_summary(panel: dict[str, Any] | None = None) -> str:
    panel = panel or _load_aim_panel()
    return str(panel.get("method_summary") or AIM_METHOD_SUMMARY)


@dataclass
class AncestryResult:
    superpopulation: str | None
    populations: dict[str, float]
    method: str
    note: str
    error: str | None = None
    markers_used: int = 0
    method_summary: str = AIM_METHOD_SUMMARY
    population_labels: dict[str, str] = field(default_factory=lambda: dict(SUPERPOPULATION_LABELS))

    def label_for(self, code: str | None) -> str:
        return superpopulation_label(code, self.population_labels)

    def percentages(self) -> dict[str, float]:
        """Normalized affinity percentages (sum ≈ 100)."""
        return population_percentages(self.populations)

    def ranked_percentages(self) -> list[tuple[str, float]]:
        """``(code, percent)`` pairs sorted descending by percentage."""
        return sorted(self.percentages().items(), key=lambda item: -item[1])

    def as_dict(self) -> dict[str, Any]:
        pct = self.percentages()
        return {
            "superpopulation": self.superpopulation,
            "superpopulation_label": self.label_for(self.superpopulation),
            "populations": self.populations,
            "percentages": pct,
            "population_labels": self.population_labels,
            "method": self.method,
            "method_summary": self.method_summary,
            "note": self.note,
            "error": self.error,
            "markers_used": self.markers_used,
        }


def _ezancestry_available() -> bool:
    try:
        import ezancestry  # noqa: F401
        return True
    except ImportError:
        return False


def _load_aim_panel(path: Path | None = None) -> dict[str, Any]:
    panel_path = path or (SHIPPED_DATA / "aim_panel.json")
    with panel_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _allele_count(genotype: str, allele: str) -> int | None:
    alleles = [a for a in genotype.upper() if a in "ACGT"]
    if not alleles:
        return None
    target = allele.upper()
    # Haploid (Y/MT-style) or single reported base → treat as 0 or 2 copies.
    if len(alleles) == 1:
        return 2 if alleles[0] == target else 0
    return sum(1 for a in alleles if a == target)


def _predict_aim_likelihood(snps: SNPs, panel: dict[str, Any] | None = None) -> AncestryResult:
    """Naive diploid likelihood under 1000 Genomes Phase 3 superpopulation AFs."""
    panel = panel or _load_aim_panel()
    labels = _panel_labels(panel)
    summary = _method_summary(panel)
    genotypes = genotype_lookup(snps)
    supers = list(panel.get("superpopulations") or ["AFR", "EUR", "EAS", "SAS", "AMR"])
    loglik = {sp: 0.0 for sp in supers}
    used = 0

    for marker in panel.get("markers") or []:
        rsid = marker.get("rsid")
        allele = marker.get("allele")
        freqs = marker.get("freq") or {}
        if not rsid or not allele:
            continue
        geno = genotypes.get(rsid)
        if not geno:
            continue
        count = _allele_count(geno, allele)
        if count is None:
            continue
        used += 1
        for sp in supers:
            p = min(1.0 - _EPS, max(_EPS, float(freqs.get(sp, 0.5))))
            # Hardy–Weinberg genotype probability for 0/1/2 copies of `allele`.
            if count == 0:
                prob = (1.0 - p) ** 2
            elif count == 1:
                prob = 2.0 * p * (1.0 - p)
            else:
                prob = p ** 2
            loglik[sp] += math.log(max(prob, _EPS))

    if used == 0:
        return AncestryResult(
            superpopulation=None,
            populations={},
            method="aim_likelihood",
            note="No AIM markers from the bundled panel were called on this chip.",
            markers_used=0,
            method_summary=summary,
            population_labels=labels,
        )

    # Softmax over log-likelihoods → normalized weights (sum to 1; UI shows %).
    max_ll = max(loglik.values())
    weights = {sp: math.exp(ll - max_ll) for sp, ll in loglik.items()}
    populations = normalize_population_weights({sp: float(weights[sp]) for sp in supers})
    best = max(populations, key=populations.get)  # type: ignore[arg-type]
    disclaimer = panel.get("disclaimer") or (
        "Exploratory AIM likelihood against 1000 Genomes superpopulations. "
        "Not a continental identity certificate."
    )
    return AncestryResult(
        superpopulation=best,
        populations=populations,
        method="aim_likelihood",
        note=(
            f"{disclaimer} Used {used} overlapping AIMs. "
            "1000 Genomes lacks a dedicated MENA cluster; West Asian samples often land near "
            "South Asian (SAS) / European (EUR)."
        ),
        markers_used=used,
        method_summary=summary,
        population_labels=labels,
    )


def _from_ezancestry_prediction(prediction: Any) -> AncestryResult:
    populations: dict[str, float] = {}
    superpop = None
    method = "snps.predict_ancestry"

    if isinstance(prediction, dict):
        superpop = (
            prediction.get("superpopulation_code")
            or prediction.get("superpopulation")
            or prediction.get("predicted_ancestry")
            or prediction.get("population_code")
        )
        df = prediction.get("ezancestry_df")
        if df is not None and hasattr(df, "iloc"):
            row = df.iloc[0]
            for key in ("AFR", "AMR", "EAS", "EUR", "SAS"):
                if key in getattr(row, "index", []) or key in getattr(row, "keys", lambda: [])():
                    try:
                        populations[key] = float(row[key])
                    except (TypeError, ValueError, KeyError):
                        pass
        probs = prediction.get("probabilities") or prediction.get("populations") or {}
        if not populations and isinstance(probs, dict):
            populations = {str(k): float(v) for k, v in probs.items() if _is_number(v)}
    elif hasattr(prediction, "to_dict"):
        data = prediction.to_dict()
        if isinstance(data, dict):
            populations = {str(k): float(v) for k, v in data.items() if _is_number(v)}
            if populations:
                superpop = max(populations, key=populations.get)  # type: ignore[arg-type]
    else:
        superpop = str(prediction)

    labels = _panel_labels()
    populations = normalize_population_weights(populations)
    if populations and not superpop:
        superpop = max(populations, key=populations.get)  # type: ignore[arg-type]
    return AncestryResult(
        superpopulation=str(superpop) if superpop else None,
        populations=populations,
        method=method,
        note=(
            "Exploratory superpopulation call against 1000 Genomes AISNPs via ezancestry. "
            "Not a continental identity certificate."
        ),
        method_summary=_method_summary(),
        population_labels=labels,
    )


def predict_ancestry(snps: SNPs) -> AncestryResult:
    """Predict 1000 Genomes-style ancestry.

    Prefers ``snps.predict_ancestry`` when ezancestry is installed. Otherwise uses a
    bundled AIM allele-frequency likelihood so the Ancestry page stays useful without
    the pandas 1.x / Python<3.12 pins that ezancestry requires.
    """
    if _ezancestry_available():
        try:
            prediction = snps.predict_ancestry()
        except Exception as exc:  # noqa: BLE001
            fallback = _predict_aim_likelihood(snps)
            fallback.note = (
                f"ezancestry failed ({exc}); fell back to bundled AIM likelihood. "
                + fallback.note
            )
            fallback.error = str(exc)
            return fallback

        if prediction is None or prediction == {}:
            return _predict_aim_likelihood(snps)
        return _from_ezancestry_prediction(prediction)

    # Default path: local AIM panel (no optional dep / no pandas pin conflict).
    result = _predict_aim_likelihood(snps)
    result.note = (
        result.note
        + " Optional ezancestry is not installed (and on Python 3.12+ cannot be: "
        'it requires Python <3.12 and pandas 1.x). For experiments: '
        'pip install -e ".[ancestry]" in a separate Python 3.10/3.11 env.'
    )
    return result


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
