from genolens.relatedness import _relationship_from_cm, compare_pair


def test_relationship_bands():
    assert "sibling" in _relationship_from_cm(2500).lower() or "Parent" in _relationship_from_cm(3500)
    assert "No shared" in _relationship_from_cm(0)


def test_compare_pair_synthetic(synthetic_genome_a, synthetic_genome_b):
    # Tiny files may not yield IBD segments; ensure API returns a structured result
    result = compare_pair(synthetic_genome_a, synthetic_genome_b)
    assert result.sample_a
    assert result.sample_b
    assert result.error is None or isinstance(result.error, str)
    assert result.shared_cm >= 0
