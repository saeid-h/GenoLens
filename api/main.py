"""Local FastAPI wrapper around the genolens package."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from genolens.ancient import ancient_status, highlight_named, load_named_remains, project_pca, rank_matches
from genolens.ancestry import predict_ancestry
from genolens.archaic import score_archaic
from genolens.haplogroups import call_haplogroups
from genolens.health import (
    HEALTH_CATEGORIES,
    PHARMA_CATEGORIES,
    TRAIT_CATEGORIES,
    WELLNESS_CATEGORIES,
    load_panel,
    match_health,
)
from genolens.ingest import load_genome
from genolens.paths import (
    default_primary,
    list_sample_files,
    resolve_sample,
    sample_id,
    sample_label,
)
from genolens.prs import score_prs
from genolens.reference import build_demo_panel, ensure_panel, panel_ready
from genolens.relatedness import (
    compare_primary_to_candidates,
    infer_pedigree,
)
from genolens.sample_meta import get_sample_meta, load_meta, upsert_sample_meta

DISCLAIMER = (
    "Exploratory only. Not medical advice, not a clinical diagnosis, and not proof of "
    "descent from any named historical person."
)

app = FastAPI(title="GenoLens API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompareRequest(BaseModel):
    primary_id: str
    candidate_ids: list[str] = Field(default_factory=list)


class FamilyTreeRequest(BaseModel):
    primary_id: str
    candidate_ids: list[str] = Field(default_factory=list)


class SampleMetaUpdate(BaseModel):
    birth_year: int | None = None
    generation: str | None = None
    display_name: str | None = None


def _path_or_404(sample_key: str) -> Path:
    path = resolve_sample(sample_key)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Sample not found: {sample_key}")
    return path


@lru_cache(maxsize=16)
def _cached_genome(path_str: str):
    return load_genome(path_str)


@app.get("/api/health")
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "genolens"}


@app.get("/api/samples")
def api_samples() -> dict[str, Any]:
    files = list_sample_files()
    primary = default_primary(files)
    meta = load_meta()
    return {
        "disclaimer": DISCLAIMER,
        "samples": [
            {
                "id": sample_id(p),
                "label": sample_label(p),
                "filename": p.name,
                "meta": meta.get("samples", {}).get(sample_id(p), {}),
            }
            for p in files
        ],
        "default_primary_id": sample_id(primary) if primary else None,
    }


@app.get("/api/samples/meta")
def api_get_all_meta() -> dict[str, Any]:
    return load_meta()


@app.put("/api/samples/{sample_key}/meta")
def api_put_meta(sample_key: str, body: SampleMetaUpdate) -> dict[str, Any]:
    _path_or_404(sample_key)
    fields = body.model_dump(exclude_unset=True)
    return {"id": sample_key, "meta": upsert_sample_meta(sample_key, fields)}


@app.get("/api/samples/{sample_key}/overview")
def api_overview(sample_key: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    return {
        "disclaimer": DISCLAIMER,
        "id": sample_id(path),
        "label": sample_label(path),
        **summary.as_dict(),
        "meta": get_sample_meta(sample_id(path)),
    }


@app.get("/api/samples/{sample_key}/ancestry")
def api_ancestry(sample_key: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    result = predict_ancestry(summary.snps)
    return {"disclaimer": DISCLAIMER, "id": sample_id(path), **result.as_dict()}


@app.get("/api/samples/{sample_key}/haplogroups")
def api_haplogroups(sample_key: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    calls = call_haplogroups(summary.snps)
    return {
        "disclaimer": DISCLAIMER,
        "id": sample_id(path),
        "Y": calls["Y"].as_dict(),
        "mt": calls["mt"].as_dict(),
    }


def _panel_response(sample_key: str, categories: frozenset[str], hub: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    panel = load_panel()
    hits = match_health(summary.snps, panel=panel, categories=categories)
    return {
        "disclaimer": panel.get("disclaimer", DISCLAIMER),
        "hub": hub,
        "id": sample_id(path),
        "markers_called": sum(1 for h in hits if h.present),
        "markers_total": len(hits),
        "hits": [h.as_dict() for h in hits],
    }


@app.get("/api/samples/{sample_key}/traits")
def api_traits(sample_key: str) -> dict[str, Any]:
    return _panel_response(sample_key, TRAIT_CATEGORIES, "traits")


@app.get("/api/samples/{sample_key}/wellness")
def api_wellness(sample_key: str) -> dict[str, Any]:
    return _panel_response(sample_key, WELLNESS_CATEGORIES, "wellness")


@app.get("/api/samples/{sample_key}/pharmacogenetics")
def api_pharma(sample_key: str) -> dict[str, Any]:
    return _panel_response(sample_key, PHARMA_CATEGORIES, "pharmacogenetics")


@app.get("/api/samples/{sample_key}/health")
def api_health_panel(sample_key: str) -> dict[str, Any]:
    return _panel_response(sample_key, HEALTH_CATEGORIES, "health")


@app.post("/api/compare")
def api_compare(body: CompareRequest) -> dict[str, Any]:
    primary = _path_or_404(body.primary_id)
    candidates: list[Path] = []
    for cid in body.candidate_ids:
        path = resolve_sample(cid)
        if path is None:
            raise HTTPException(status_code=404, detail=f"Candidate not found: {cid}")
        candidates.append(path)
    pairs = compare_primary_to_candidates(primary, candidates)
    return {
        "disclaimer": DISCLAIMER,
        "primary_id": sample_id(primary),
        "primary_label": sample_label(primary),
        "pairs": [p.as_dict() for p in pairs],
    }


@app.post("/api/family-tree")
def api_family_tree(body: FamilyTreeRequest) -> dict[str, Any]:
    primary = _path_or_404(body.primary_id)
    candidates = [_path_or_404(cid) for cid in body.candidate_ids]
    pairs = compare_primary_to_candidates(primary, candidates)
    # Also compare among candidates when small set (≤8 including primary)
    from genolens.relatedness import compare_all_pairs

    selected = [primary] + [c for c in candidates if c.resolve() != primary.resolve()]
    if 2 < len(selected) <= 8:
        # include candidate×candidate for better triangulation
        extra = compare_all_pairs(selected)
        seen = {(p.sample_a, p.sample_b) for p in pairs}
        for p in extra:
            key = (p.sample_a, p.sample_b)
            if key not in seen and (p.sample_b, p.sample_a) not in seen:
                pairs.append(p)

    sex_by_label: dict[str, str | None] = {}
    birth_by_label: dict[str, int | None] = {}
    for path in selected:
        lab = sample_label(path)
        sid = sample_id(path)
        try:
            sex_by_label[lab] = _cached_genome(str(path)).sex
        except Exception:  # noqa: BLE001
            sex_by_label[lab] = None
        meta = get_sample_meta(sid)
        by = meta.get("birth_year")
        birth_by_label[lab] = int(by) if by is not None else None

    pedigree = infer_pedigree(pairs, sex_by_label=sex_by_label, birth_year_by_label=birth_by_label)
    return {
        "disclaimer": DISCLAIMER,
        "primary_id": sample_id(primary),
        "pairs": [p.as_dict() for p in pairs],
        "pedigree": pedigree.as_dict(),
    }


@app.get("/api/samples/{sample_key}/ancient")
def api_ancient(sample_key: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    status = ancient_status()
    if not panel_ready():
        ensure_panel()
        if not panel_ready():
            build_demo_panel()
    ranked = rank_matches(summary.snps, min_snps=1)
    individuals = ranked.get("individuals") or []
    groups_df = ranked.get("groups")
    groups = (
        groups_df.head(25).to_dict(orient="records")
        if hasattr(groups_df, "to_dict")
        else []
    )
    pca = project_pca(summary.snps)
    ann = pca.get("annotation")
    pca_out = {
        "user": pca.get("user"),
        "explained_variance": pca.get("explained_variance"),
        "is_demo": pca.get("is_demo"),
        "points": (
            ann[["genetic_id", "group", "PC1", "PC2"]].head(200).to_dict(orient="records")
            if hasattr(ann, "to_dict") and "PC1" in getattr(ann, "columns", [])
            else []
        ),
    }
    named = highlight_named(individuals, load_named_remains())
    return {
        "disclaimer": DISCLAIMER,
        "id": sample_id(path),
        "status": status,
        "ranked": {
            "individuals": [m.as_dict() for m in individuals],
            "groups": groups,
            "user_called_snps": ranked.get("user_called_snps"),
            "panel_snps": ranked.get("panel_snps"),
            "is_demo": ranked.get("is_demo"),
        },
        "pca": pca_out,
        "named_remains": named,
    }


@app.get("/api/samples/{sample_key}/archaic")
def api_archaic(sample_key: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    return {"id": sample_id(path), **score_archaic(summary.snps)}


@app.get("/api/samples/{sample_key}/prs")
def api_prs(sample_key: str) -> dict[str, Any]:
    path = _path_or_404(sample_key)
    summary = _cached_genome(str(path))
    return {"id": sample_id(path), **score_prs(summary.snps)}


@app.get("/api/reference/status")
def api_reference_status() -> dict[str, Any]:
    from genolens.reference_catalog import aadr_download_hint, pgs_catalog_status

    return {
        "disclaimer": DISCLAIMER,
        "ancient": ancient_status(),
        "aadr": aadr_download_hint(),
        "prs": pgs_catalog_status(),
    }


def run() -> None:
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run()
