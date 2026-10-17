from pathlib import Path

from genolens.haplogroups import call_haplogroups, load_tree
from genolens.ingest import load_genome


def test_mt_tree_has_position_markers():
    tree = load_tree()
    mt = tree["mt"]
    assert any(m.get("pos") for m in mt)


def test_mt_resolves_on_real_file_if_present():
    path = Path("data/genome_Saeid_Hosseinipoor_v5_Full_20220131131756.txt")
    if not path.is_file():
        return
    summary = load_genome(path)
    calls = call_haplogroups(summary.snps)
    assert calls["mt"].markers_called > 0
    # Soft-pass root should allow a macrohaplogroup when defining SNPs match
    assert calls["mt"].haplogroup is not None
    assert "U" in calls["mt"].path or calls["mt"].haplogroup in {"N", "R", "U", "H", "JT", "J", "T", "K", "M"}
