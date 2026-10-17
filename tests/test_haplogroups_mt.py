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


def test_y_reaches_beyond_bt_on_real_file_if_present():
    """Regression: CT was wrongly mapped to M45; Saeid should reach CT/CF/P, not stop at BT."""
    path = Path("data/genome_Saeid_Hosseinipoor_v5_Full_20220131131756.txt")
    if not path.is_file():
        return
    calls = call_haplogroups(load_genome(path).snps)
    y = calls["Y"]
    assert y.haplogroup is not None
    assert y.haplogroup != "BT"
    assert "CT" in y.path
    assert y.haplogroup in {"CT", "CF", "F", "K", "P", "R", "R1", "R1a", "R1b", "Q"}
