from pathlib import Path

from snps import SNPs

from genolens.archaic import score_archaic
from genolens.prs import score_prs


def _tiny_snps(tmp_path: Path) -> SNPs:
    path = tmp_path / "tiny.txt"
    path.write_text(
        "# 23andMe\n"
        "rsid\tchromosome\tposition\tgenotype\n"
        "rs9939609\t16\t53820527\tAA\n"
        "rs17822931\t16\t48258198\tTT\n"
    )
    return SNPs(str(path))


def test_archaic_and_prs_run(tmp_path):
    snps = _tiny_snps(tmp_path)
    archaic = score_archaic(snps)
    assert "hits" in archaic
    prs = score_prs(snps)
    assert prs["scores"]
    assert any(s["id"] == "DEMO_BMI" for s in prs["scores"])
