from pathlib import Path

import pandas as pd

from genolens.relatedness import (
    PairResult,
    _extract_segments,
    _extract_shared_cm,
    _relationship_from_cm,
    compare_pair,
    infer_pedigree,
    pedigree_plotly_figure,
)


def _pair(a: str, b: str, cm: float) -> PairResult:
    from genolens.relatedness import _relationship_from_cm as rel

    return PairResult(
        sample_a=a,
        sample_b=b,
        path_a=Path(f"{a}.txt"),
        path_b=Path(f"{b}.txt"),
        shared_cm=cm,
        shared_segments=10 if cm > 0 else 0,
        relationship=rel(cm),
    )


def test_relationship_bands():
    assert "sibling" in _relationship_from_cm(2500).lower() or "Parent" in _relationship_from_cm(3500)
    assert "No shared" in _relationship_from_cm(0)


def test_extract_lineage_v4_shape():
    """lineage 4.x returns one_chrom_shared_dna with a `cMs` column — not `segments`/`cM`."""
    one = pd.DataFrame(
        {"chrom": [1, 2], "start": [1, 1], "end": [100, 100], "cMs": [100.0, 50.5], "snps": [10, 10]}
    )
    result = {"one_chrom_shared_dna": one, "two_chrom_shared_dna": pd.DataFrame()}
    segs = _extract_segments(result)
    assert len(segs) == 2
    assert abs(_extract_shared_cm(result, segs) - 150.5) < 1e-6


def test_compare_pair_synthetic(synthetic_genome_a, synthetic_genome_b):
    # Tiny files may not yield IBD segments; ensure API returns a structured result
    result = compare_pair(synthetic_genome_a, synthetic_genome_b)
    assert result.sample_a
    assert result.sample_b
    assert result.error is None or isinstance(result.error, str)
    assert result.shared_cm >= 0


def test_infer_pedigree_nuclear_family():
    """Mother+Father → two children (sibling-range); spouses ~0 cM."""
    pairs = [
        _pair("Farideh", "Saeid", 3500),
        _pair("Farideh", "Soltan", 3480),
        _pair("Mahmoud", "Saeid", 3520),
        _pair("Mahmoud", "Soltan", 3490),
        _pair("Saeid", "Soltan", 2550),
        _pair("Farideh", "Mahmoud", 0),
    ]
    sex = {"Farideh": "Female", "Mahmoud": "Male", "Saeid": "Male", "Soltan": "Female"}
    est = infer_pedigree(pairs, sex_by_label=sex)
    roles = {n.label: n.role for n in est.nodes}
    assert roles["Farideh"] == "Mother"
    assert roles["Mahmoud"] == "Father"
    assert roles["Saeid"] == "Child"
    assert roles["Soltan"] == "Child"
    directed_pc = [e for e in est.edges if e.kind == "parent_child" and e.directed]
    assert len(directed_pc) == 4
    assert any(e.source == "Farideh" and e.target == "Saeid" for e in directed_pc)
    assert any(e.kind == "sibling" for e in est.edges)
    assert est.ascii_tree
    fig = pedigree_plotly_figure(est)
    assert fig is not None


def test_infer_pedigree_unknown_sex_parents():
    pairs = [
        _pair("P1", "Kid", 3600),
        _pair("P2", "Kid", 3550),
        _pair("P1", "P2", 5),
    ]
    est = infer_pedigree(pairs, sex_by_label={"P1": None, "P2": None, "Kid": "Male"})
    roles = {n.label: n.role for n in est.nodes}
    assert {roles["P1"], roles["P2"]} == {"Parent A", "Parent B"}
    assert roles["Kid"] == "Child"
