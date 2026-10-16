from genolens.ancient import highlight_named, load_named_remains, project_pca, rank_matches
from genolens.ingest import load_genome
from genolens.reference import build_demo_panel, load_panel, panel_ready


def test_demo_panel_roundtrip(tmp_path):
    dest = build_demo_panel(out_dir=tmp_path / "ref", n_snps=30, n_samples=8)
    assert panel_ready(tmp_path / "ref")
    panel = load_panel(tmp_path / "ref")
    assert panel["genotypes"].shape == (30, 8)
    assert len(panel["annotation"]) == 8


def test_rank_and_pca(synthetic_genome_a, tmp_path):
    # Demo panel rsIDs do not overlap the synthetic genome — expect empty rankings, stable schema
    build_demo_panel(out_dir=tmp_path / "ref", n_snps=40, n_samples=10)
    summary = load_genome(synthetic_genome_a)
    ranked = rank_matches(summary.snps, panel_base=tmp_path / "ref", min_snps=1)
    assert "individuals" in ranked
    assert list(ranked["groups"].columns) == [
        "group",
        "mean_distance",
        "n_individuals",
        "median_n_snps",
    ]
    pca = project_pca(summary.snps, panel_base=tmp_path / "ref")
    assert "PC1" in pca["user"]
    named = highlight_named(ranked["individuals"], load_named_remains())
    assert any(row["name"] == "Ötzi the Iceman" for row in named)


def test_named_remains_mentions_missing_royals():
    data = load_named_remains()
    assert data["missing_royals"]
    assert any("Achaemenid" in line for line in data["missing_royals"])
