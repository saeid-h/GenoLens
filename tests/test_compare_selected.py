from pathlib import Path

from genolens.relatedness import compare_primary_to_candidates, _edge_kind, _relationship_from_sharing


def test_edge_kind_uses_ibd2():
    assert _edge_kind(3500, ibd2_cm=0) == "parent_child"
    # Modest IBD2 in the parent/child cM band is treated as noise, not sibling.
    assert _edge_kind(3500, ibd2_cm=267) == "parent_child"
    assert _edge_kind(3500, ibd2_cm=600) == "sibling"
    assert _edge_kind(2500, ibd2_cm=150) == "sibling"
    # Sibling cM band stays sibling even with low/unknown IBD2 (parent–child is ≥3400).
    assert _edge_kind(2500, ibd2_cm=5) == "sibling"
    assert _edge_kind(2500, ibd2_cm=0) == "sibling"


def test_age_gap_demotes_sibling_band():
    from pathlib import Path
    from genolens.relatedness import PairResult, infer_pedigree, _relationship_from_cm

    def pair(a: str, b: str, cm: float, ibd2: float = 0.0) -> PairResult:
        return PairResult(
            sample_a=a,
            sample_b=b,
            path_a=Path(f"{a}.txt"),
            path_b=Path(f"{b}.txt"),
            shared_cm=cm,
            shared_segments=10,
            relationship=_relationship_from_cm(cm),
            ibd2_cm=ibd2,
        )

    # Grandparent–grandchild can land in sibling cM band; ages should reorient.
    pairs = [pair("Grandma", "Kid", 2300, ibd2=0)]
    est = infer_pedigree(
        pairs,
        birth_year_by_label={"Grandma": 1930, "Kid": 1978},
    )
    directed = [e for e in est.edges if e.kind == "parent_child" and e.directed]
    assert any(e.source == "Grandma" and e.target == "Kid" for e in directed)


def test_relationship_text_mentions_ibd2():
    assert "sibling" in _relationship_from_sharing(2500, 200).lower()
    assert "parent" in _relationship_from_sharing(3500, 0).lower()


def test_compare_primary_skips_self(tmp_path):
    # Use real files when present; otherwise skip
    data = Path("data")
    files = sorted(data.glob("genome_*.txt"))
    if len(files) < 2:
        return
    pairs = compare_primary_to_candidates(files[0], files[:3])
    assert all(p.path_a.resolve() != p.path_b.resolve() for p in pairs)
    assert len(pairs) >= 1
