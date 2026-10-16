"""Load and summarize consumer genotype files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from snps import SNPs


@dataclass
class GenomeSummary:
    path: Path
    source: str
    build: int | None
    assembly: str | None
    count: int
    sex: str | None
    chip: str | None
    snps: SNPs

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "source": self.source,
            "build": self.build,
            "assembly": self.assembly,
            "count": self.count,
            "sex": self.sex,
            "chip": self.chip,
        }


def load_genome(path: str | Path) -> GenomeSummary:
    """Parse a 23andMe (or other supported) raw data file."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Genome file not found: {path}")

    snps = SNPs(str(path))
    if snps.snps is None or snps.snps.empty:
        raise ValueError(f"No SNPs loaded from {path}")

    chip = None
    for attr in ("chip", "chip_version", "deduced_genotype"):
        value = getattr(snps, attr, None)
        if value:
            chip = str(value)
            break

    sex = None
    try:
        sex = snps.get_sex()
    except Exception:
        sex = getattr(snps, "sex", None)

    return GenomeSummary(
        path=path,
        source=str(getattr(snps, "source", "unknown") or "unknown"),
        build=getattr(snps, "build", None),
        assembly=getattr(snps, "assembly", None),
        count=int(getattr(snps, "count", len(snps.snps))),
        sex=str(sex) if sex else None,
        chip=chip,
        snps=snps,
    )


def genotype_lookup(snps: SNPs) -> dict[str, str]:
    """Map rsid -> genotype string (e.g. 'AG')."""
    frame = snps.snps
    if frame is None or frame.empty:
        return {}
    if "genotype" not in frame.columns:
        return {}
    return {
        str(rsid): str(geno)
        for rsid, geno in frame["genotype"].dropna().items()
        if geno and geno not in {"--", "nan"}
    }
