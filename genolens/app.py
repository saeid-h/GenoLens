"""GenoLens Streamlit UI."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from genolens.ancient import (
    ancient_status,
    highlight_named,
    load_named_remains,
    project_pca,
    rank_matches,
)
from genolens.ancestry import predict_ancestry
from genolens.haplogroups import call_haplogroups
from genolens.health import load_panel, match_health
from genolens.ingest import load_genome
from genolens.paths import DATA_DIR, default_primary, list_sample_files, sample_label
from genolens.reference import build_demo_panel, ensure_panel, panel_ready
from genolens.relatedness import compare_pair, relatedness_matrix

DISCLAIMER = (
    "**Exploratory only.** Not medical advice, not a clinical diagnosis, and not proof of "
    "descent from any named historical person. Microarray data covers a tiny fraction of the genome. "
    "Ancient matches are population affinity signals on overlapping SNPs."
)


def _init_state() -> None:
    if "primary_path" not in st.session_state:
        primary = default_primary()
        st.session_state.primary_path = str(primary) if primary else ""
    if "extra_path" not in st.session_state:
        st.session_state.extra_path = ""


@st.cache_resource(show_spinner="Loading genome…")
def _cached_genome(path: str):
    return load_genome(path)


def _sidebar() -> Path | None:
    st.sidebar.title("GenoLens")
    st.sidebar.caption("Local DNA lens — files never leave this machine.")

    samples = list_sample_files()
    labels = {sample_label(p): str(p) for p in samples}
    options = list(labels.keys())
    if not options:
        st.sidebar.warning(f"No `*.txt` genome files in `{DATA_DIR}`.")
    else:
        default_path = st.session_state.primary_path
        default_idx = 0
        for i, lab in enumerate(options):
            if labels[lab] == default_path:
                default_idx = i
                break
        chosen = st.sidebar.selectbox("Primary sample", options, index=default_idx)
        st.session_state.primary_path = labels[chosen]

    extra = st.sidebar.text_input(
        "Or path to another 23andMe file",
        value=st.session_state.extra_path,
        help="Absolute path on this machine. Nothing is uploaded.",
    )
    st.session_state.extra_path = extra.strip()
    if st.session_state.extra_path:
        return Path(st.session_state.extra_path)
    if st.session_state.primary_path:
        return Path(st.session_state.primary_path)
    return None


def page_overview(path: Path) -> None:
    st.header("Overview")
    st.info(DISCLAIMER)
    try:
        summary = _cached_genome(str(path))
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load {path}: {exc}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SNPs", f"{summary.count:,}")
    c2.metric("Build", str(summary.build or "—"))
    c3.metric("Source", summary.source)
    c4.metric("Sex (derived)", summary.sex or "—")
    st.write(f"**File:** `{summary.path}`")
    st.write(f"**Assembly:** {summary.assembly or '—'}  |  **Chip:** {summary.chip or '—'}")
    st.caption("Default primary sample prefers the Saeid Hosseinipoor v5 export when present.")


def page_health(path: Path) -> None:
    st.header("Health & traits")
    st.warning(load_panel().get("disclaimer", DISCLAIMER))
    summary = _cached_genome(str(path))
    hits = match_health(summary.snps)
    rows = [h.as_dict() for h in hits]
    df = pd.DataFrame(rows)
    present = int(df["present"].sum()) if not df.empty else 0
    st.write(f"Panel markers called on this file: **{present}** / {len(df)}")
    st.dataframe(
        df[["rsid", "gene", "category", "genotype", "note", "summary", "source"]],
        use_container_width=True,
        hide_index=True,
    )


def page_compare(path: Path) -> None:
    st.header("Compare")
    st.info("Pairwise shared DNA via the `lineage` library. Rough relationship bands are approximate.")
    samples = list_sample_files()
    if len(samples) < 2:
        st.warning("Need at least two genome files in `data/` for a matrix.")
        other = st.text_input("Path to a second genome file")
        if other and Path(other).is_file():
            result = compare_pair(path, Path(other))
            _show_pair(result)
        return

    with st.spinner("Computing relatedness matrix (can take a few minutes)…"):
        try:
            matrix = relatedness_matrix(samples)
            st.subheader("Shared cM matrix")
            st.dataframe(matrix.style.format("{:.1f}", na_rep="—"), use_container_width=True)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Matrix failed: {exc}")

    labels = [sample_label(p) for p in samples]
    paths_by_label = {sample_label(p): p for p in samples}
    primary_label = sample_label(path) if path in samples else labels[0]
    a = st.selectbox("Sample A", labels, index=labels.index(primary_label) if primary_label in labels else 0)
    b_options = [x for x in labels if x != a]
    b = st.selectbox("Sample B", b_options, index=0)
    if st.button("Show pair detail", type="primary"):
        with st.spinner("Comparing pair…"):
            result = compare_pair(paths_by_label[a], paths_by_label[b])
            _show_pair(result)


def _show_pair(result) -> None:
    if result.error:
        st.error(result.error)
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Shared cM", f"{result.shared_cm:.1f}")
    c2.metric("Segments", result.shared_segments)
    c3.metric("Estimate", result.relationship or "—")
    if result.chrom_summary is not None and not result.chrom_summary.empty:
        st.subheader("Per-chromosome summary")
        st.dataframe(result.chrom_summary, use_container_width=True, hide_index=True)
    if result.segments is not None and not result.segments.empty:
        st.subheader("Shared segments")
        st.dataframe(result.segments, use_container_width=True, hide_index=True)


def page_ancestry(path: Path) -> None:
    st.header("Ancestry & haplogroups")
    summary = _cached_genome(str(path))

    st.subheader("Superpopulation (ezancestry)")
    with st.spinner("Predicting ancestry…"):
        anc = predict_ancestry(summary.snps)
    if anc.error:
        st.warning(anc.note)
        st.caption(anc.error)
    else:
        st.write(f"**Call:** {anc.superpopulation or '—'}  ({anc.method})")
        st.caption(anc.note)
        if anc.populations:
            st.dataframe(
                pd.DataFrame(
                    [{"population": k, "score": v} for k, v in sorted(anc.populations.items(), key=lambda x: -x[1])]
                ),
                use_container_width=True,
                hide_index=True,
            )

    st.subheader("Haplogroups (shallow microarray tree)")
    calls = call_haplogroups(summary.snps)
    for key in ("Y", "mt"):
        call = calls[key]
        st.markdown(
            f"**{key}:** `{call.haplogroup or 'unresolved'}`  "
            f"— path: {' → '.join(call.path) if call.path else '—'}  "
            f"({call.markers_called}/{call.markers_tested} markers called)"
        )
        st.caption(call.note)


def page_ancient(path: Path) -> None:
    st.header("Ancient affinity")
    status = ancient_status()
    st.info(status.get("disclaimer") or DISCLAIMER)
    for line in status.get("missing_royals", []):
        st.caption(f"• {line}")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Ensure demo reference panel"):
            dest = build_demo_panel()
            st.success(f"Demo panel ready at {dest}")
            st.cache_data.clear()
    with col_b:
        st.write("Panel ready:" , "✅" if panel_ready() else "❌ (will auto-create demo)")

    ensure_panel(use_demo_if_missing=True)
    summary = _cached_genome(str(path))

    with st.spinner("Ranking ancient matches…"):
        ranked = rank_matches(summary.snps)
    if ranked.get("is_demo"):
        st.warning(
            "Using the **synthetic demo panel**. Download AADR v66 1240K and run prepare "
            "for real ancient matches (see README)."
        )

    st.write(
        f"User SNPs overlapping panel: **{ranked['user_called_snps']}** / {ranked['panel_snps']}"
    )
    ind_df = pd.DataFrame([m.as_dict() for m in ranked["individuals"]])
    st.subheader("Closest individuals")
    st.dataframe(ind_df, use_container_width=True, hide_index=True)

    st.subheader("Closest groups")
    st.dataframe(ranked["groups"], use_container_width=True, hide_index=True)

    named = highlight_named(ranked["individuals"], load_named_remains())
    st.subheader("Named remains checklist")
    st.dataframe(pd.DataFrame(named), use_container_width=True, hide_index=True)

    with st.spinner("PCA projection (fit on reference, project user)…"):
        pca = project_pca(summary.snps)
    ann = pca["annotation"]
    fig = px.scatter(
        ann,
        x="PC1",
        y="PC2",
        color="group" if "group" in ann.columns else None,
        hover_data=[c for c in ("genetic_id", "country", "date") if c in ann.columns],
        title="PCA of reference samples (user projected)",
    )
    fig.add_scatter(
        x=[pca["user"]["PC1"]],
        y=[pca["user"]["PC2"]],
        mode="markers+text",
        text=["You"],
        textposition="top center",
        marker={"size": 14, "symbol": "star", "color": "black"},
        name="You",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Variance explained: "
        + ", ".join(f"PC{i+1}={v:.1%}" for i, v in enumerate(pca["explained_variance"]))
    )


def main() -> None:
    st.set_page_config(page_title="GenoLens", page_icon="🧬", layout="wide")
    _init_state()
    path = _sidebar()
    pages = {
        "Overview": page_overview,
        "Health": page_health,
        "Compare": page_compare,
        "Ancestry": page_ancestry,
        "Ancient": page_ancient,
    }
    page = st.sidebar.radio("Page", list(pages.keys()))
    if path is None or not path.is_file():
        st.title("GenoLens")
        st.write("Add 23andMe raw `*.txt` files under `data/` (gitignored) and pick one in the sidebar.")
        return
    pages[page](path)


if __name__ == "__main__":
    main()
