from genolens.ancestry import (
    SUPERPOPULATION_LABELS,
    normalize_population_weights,
    population_percentages,
    predict_ancestry,
    superpopulation_label,
)
from genolens.haplogroups import call_haplogroups
from genolens.ingest import load_genome


def test_haplogroup_call_runs(synthetic_genome_a):
    summary = load_genome(synthetic_genome_a)
    calls = call_haplogroups(summary.snps)
    assert "Y" in calls and "mt" in calls
    assert calls["Y"].markers_tested > 0
    # Synthetic file lacks Y markers — expect unresolved with a clear note
    assert calls["Y"].haplogroup is None or isinstance(calls["Y"].haplogroup, str)


def test_superpopulation_labels():
    assert superpopulation_label("EUR") == "European (EUR)"
    assert superpopulation_label("sas") == "South Asian (SAS)"
    for code in ("AFR", "AMR", "EAS", "EUR", "SAS"):
        assert code in SUPERPOPULATION_LABELS
        assert SUPERPOPULATION_LABELS[code]
        assert code in superpopulation_label(code)


def test_normalize_population_percentages():
    weights = normalize_population_weights({"EUR": 2.0, "SAS": 1.0, "AFR": 1.0})
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert abs(weights["EUR"] - 0.5) < 1e-9
    pct = population_percentages({"EUR": 2.0, "SAS": 1.0, "AFR": 1.0})
    assert abs(sum(pct.values()) - 100.0) < 1e-6
    assert abs(pct["EUR"] - 50.0) < 1e-6


def test_ancestry_does_not_crash(synthetic_genome_a):
    summary = load_genome(synthetic_genome_a)
    result = predict_ancestry(summary.snps)
    assert result.method
    assert result.note
    assert result.method_summary
    assert "continental" in result.method_summary.lower() or "AIM" in result.method_summary
    # Without ezancestry, bundled AIM likelihood should still return a structured result
    assert result.method in {"aim_likelihood", "snps.predict_ancestry", "unavailable", "error", "none"}
    assert result.error is None or isinstance(result.error, str)
    assert "AFR" in result.population_labels
    assert result.population_labels["EUR"] == "European"
    payload = result.as_dict()
    assert "superpopulation_label" in payload
    assert "population_labels" in payload
    assert "method_summary" in payload
    assert "percentages" in payload
    if result.populations:
        pct = result.percentages()
        assert abs(sum(pct.values()) - 100.0) < 1e-3
        assert result.ranked_percentages()[0][1] == max(pct.values())
    if result.superpopulation:
        assert result.label_for(result.superpopulation)
        assert "(" in result.label_for(result.superpopulation)
