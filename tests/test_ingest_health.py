from genolens.health import match_health
from genolens.ingest import genotype_lookup, load_genome
from genolens.paths import sample_label


def test_load_synthetic_genome(synthetic_genome_a):
    summary = load_genome(synthetic_genome_a)
    assert summary.count >= 5
    assert summary.build in (37, None) or summary.build == 37
    lookup = genotype_lookup(summary.snps)
    assert "rs1801133" in lookup
    assert lookup["rs1801133"] == "AG"


def test_health_panel_matches(synthetic_genome_a):
    summary = load_genome(synthetic_genome_a)
    hits = match_health(summary.snps)
    present = [h for h in hits if h.present]
    assert len(present) >= 5
    mthfr = next(h for h in hits if h.rsid == "rs1801133")
    assert mthfr.genotype == "AG"
    assert "panel note" not in mthfr.note.lower() or "copy" in mthfr.note.lower() or "allele" in mthfr.note.lower()


def test_sample_label():
    from pathlib import Path

    assert "Saeid" in sample_label(Path("genome_Saeid_Hosseinipoor_v5_Full_20220131131756.txt"))
