"""Broad ancestry prediction via snps + optional ezancestry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from snps import SNPs


@dataclass
class AncestryResult:
    superpopulation: str | None
    populations: dict[str, float]
    method: str
    note: str
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "superpopulation": self.superpopulation,
            "populations": self.populations,
            "method": self.method,
            "note": self.note,
            "error": self.error,
        }


def _ezancestry_available() -> bool:
    try:
        import ezancestry  # noqa: F401
        return True
    except ImportError:
        return False


def predict_ancestry(snps: SNPs) -> AncestryResult:
    """Predict 1000 Genomes-style ancestry when ezancestry is installed.

    Core GenoLens deps intentionally omit ezancestry because it pins pandas 1.x
    and conflicts with Streamlit on Python 3.9. Soft-import and degrade cleanly.
    """
    if not _ezancestry_available():
        return AncestryResult(
            superpopulation=None,
            populations={},
            method="unavailable",
            note=(
                "ezancestry is not installed (optional). "
                "Core GenoLens skips it because it pins pandas 1.x and conflicts "
                "with Streamlit. For ancestry-only experiments: "
                "pip install 'genolens[ancestry]' in a separate environment."
            ),
        )

    try:
        prediction = snps.predict_ancestry()
    except Exception as exc:  # noqa: BLE001
        return AncestryResult(
            superpopulation=None,
            populations={},
            method="error",
            note="Ancestry prediction failed.",
            error=str(exc),
        )

    if prediction is None:
        return AncestryResult(
            superpopulation=None,
            populations={},
            method="none",
            note="Ancestry prediction returned no result.",
        )

    populations: dict[str, float] = {}
    superpop = None
    method = "snps.predict_ancestry"

    if isinstance(prediction, dict):
        superpop = prediction.get("superpopulation") or prediction.get("predicted_ancestry")
        probs = prediction.get("probabilities") or prediction.get("populations") or {}
        if isinstance(probs, dict):
            populations = {str(k): float(v) for k, v in probs.items()}
    elif hasattr(prediction, "to_dict"):
        data = prediction.to_dict()
        if isinstance(data, dict):
            populations = {str(k): float(v) for k, v in data.items() if _is_number(v)}
            if populations:
                superpop = max(populations, key=populations.get)  # type: ignore[arg-type]
    else:
        superpop = str(prediction)

    return AncestryResult(
        superpopulation=str(superpop) if superpop else None,
        populations=populations,
        method=method,
        note="Exploratory superpopulation call against 1000 Genomes AISNPs. Not a continental identity certificate.",
    )


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
