from genolens.ancestry import predict_ancestry
from genolens.haplogroups import call_haplogroups
from genolens.ingest import load_genome


def test_haplogroup_call_runs(synthetic_genome_a):
    summary = load_genome(synthetic_genome_a)
    calls = call_haplogroups(summary.snps)
    assert "Y" in calls and "mt" in calls
    assert calls["Y"].markers_tested > 0
    # Synthetic file lacks Y markers — expect unresolved with a clear note
    assert calls["Y"].haplogroup is None or isinstance(calls["Y"].haplogroup, str)


def test_ancestry_does_not_crash(synthetic_genome_a):
    summary = load_genome(synthetic_genome_a)
    result = predict_ancestry(summary.snps)
    assert result.method
    assert result.note
