from pathlib import Path

from genolens.relatedness import compare_primary_to_candidates, _edge_kind, _relationship_from_sharing


def test_edge_kind_uses_ibd2():
    assert _edge_kind(3500, ibd2_cm=0) == "parent_child"
    assert _edge_kind(3500, ibd2_cm=400) == "sibling"
    assert _edge_kind(2500, ibd2_cm=150) == "sibling"
    # Sibling cM band stays sibling even with low/unknown IBD2 (parent–child is ≥3400).
    assert _edge_kind(2500, ibd2_cm=5) == "sibling"
    assert _edge_kind(2500, ibd2_cm=0) == "sibling"


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
