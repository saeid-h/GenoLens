#!/usr/bin/env python3
"""Download a chip-friendly PGS Catalog subset into data/reference/prs/catalog.json.

Does **not** upload genomes. Does **not** download the entire catalog (~7k scores,
many with 10k–1M+ SNPs). Default: diverse traits, ≤100 variants each, capped count.

Example:
  .venv/bin/python scripts/download_pgs_catalog.py
  .venv/bin/python scripts/download_pgs_catalog.py --max-variants 200 --limit 150
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "data" / "reference" / "prs" / "catalog.json"
LIST_URL = "https://www.pgscatalog.org/rest/score/all?limit=50"


def _get_json(url: str, timeout: int = 90) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": "GenoLens-local/0.0.0 (research; no genome upload)"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_bytes(url: str, timeout: int = 120) -> bytes:
    req = Request(url, headers={"User-Agent": "GenoLens-local/0.0.0 (research; no genome upload)"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def iter_score_metadata(max_pages: int | None = None) -> list[dict[str, Any]]:
    url: str | None = LIST_URL
    out: list[dict[str, Any]] = []
    page = 0
    while url:
        page += 1
        if max_pages is not None and page > max_pages:
            break
        data = _get_json(url)
        out.extend(data.get("results") or [])
        url = data.get("next")
        if page % 20 == 0 or not url:
            print(f"  listed {len(out)} / {data.get('count')} scores…", flush=True)
        time.sleep(0.08)
    return out


def parse_scoring_file(raw: bytes) -> list[dict[str, Any]]:
    text = gzip.decompress(raw).decode("utf-8", errors="replace")
    header: list[str] | None = None
    variants: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if header is None:
            header = line.strip().split("\t")
            continue
        cols = line.strip().split("\t")
        row = {header[i]: cols[i] if i < len(cols) else "" for i in range(len(header))}
        rsid = (row.get("rsID") or row.get("rsid") or "").strip()
        if not rsid or not rsid.startswith("rs"):
            continue
        allele = (row.get("effect_allele") or "").strip()
        weight_s = (row.get("effect_weight") or row.get("weight") or "").strip()
        if not allele or not weight_s:
            continue
        try:
            weight = float(weight_s)
        except ValueError:
            continue
        variants.append({"rsid": rsid, "effect_allele": allele, "weight": weight})
    return variants


def citation_from_meta(meta: dict[str, Any]) -> str:
    pub = meta.get("publication") or {}
    bits = [
        pub.get("firstauthor"),
        pub.get("journal"),
        str(pub.get("date_publication") or "")[:4] or None,
        f"doi:{pub['doi']}" if pub.get("doi") else None,
        meta.get("id"),
    ]
    return " · ".join(str(b) for b in bits if b)


def pick_diverse(metas: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Prefer one score per trait_reported, then fill remaining slots by size."""
    by_trait: dict[str, dict[str, Any]] = {}
    for m in sorted(metas, key=lambda x: (x.get("variants_number") or 0, x.get("id") or "")):
        trait = (m.get("trait_reported") or m.get("id") or "").strip().lower()
        if trait not in by_trait:
            by_trait[trait] = m
    chosen = list(by_trait.values())
    chosen.sort(key=lambda x: (x.get("variants_number") or 0, x.get("id") or ""))
    if len(chosen) >= limit:
        return chosen[:limit]
    seen = {m["id"] for m in chosen}
    for m in sorted(metas, key=lambda x: (x.get("variants_number") or 0, x.get("id") or "")):
        if m["id"] in seen:
            continue
        chosen.append(m)
        seen.add(m["id"])
        if len(chosen) >= limit:
            break
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--max-variants", type=int, default=100)
    ap.add_argument("--limit", type=int, default=80, help="Max scores to keep (default 80)")
    ap.add_argument("--max-pages", type=int, default=0, help="Debug: only N list pages (0=all)")
    ap.add_argument("--sleep", type=float, default=0.15)
    args = ap.parse_args()

    print("Listing PGS Catalog scores…", flush=True)
    metas = iter_score_metadata(max_pages=args.max_pages or None)
    eligible = [
        m
        for m in metas
        if (m.get("variants_number") or 0) <= args.max_variants and m.get("ftp_scoring_file")
    ]
    candidates = pick_diverse(eligible, args.limit)
    print(
        f"Eligible ≤{args.max_variants} variants: {len(eligible)}; "
        f"downloading diverse subset: {len(candidates)}",
        flush=True,
    )

    scores: list[dict[str, Any]] = []
    errors = 0
    for meta in candidates:
        pgs_id = meta["id"]
        trait = meta.get("trait_reported") or pgs_id
        try:
            raw = _get_bytes(meta["ftp_scoring_file"])
            variants = parse_scoring_file(raw)
            if not variants:
                print(f"  skip {pgs_id}: no rsID rows", flush=True)
                continue
            scores.append(
                {
                    "id": pgs_id,
                    "trait": trait,
                    "trait_plain": trait,
                    "what_it_is": (
                        f"Open PGS Catalog score {pgs_id} ({meta.get('name') or ''}). "
                        f"Weighted allele sum over {len(variants)} rsID variants present in the file."
                    ),
                    "what_it_is_not": (
                        "Not a diagnosis, not calibrated clinical risk, and not a body measurement. "
                        "Ancestry of the source GWAS may not match yours."
                    ),
                    "citation": citation_from_meta(meta),
                    "variants_number_catalog": meta.get("variants_number"),
                    "variants": variants,
                }
            )
            print(f"  [{len(scores)}] {pgs_id} · {trait[:55]} · {len(variants)} rsIDs", flush=True)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            print(f"  error {pgs_id}: {exc}", flush=True)
        time.sleep(args.sleep)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    catalog = {
        "mode": "catalog",
        "disclaimer": (
            "Exploratory polygenic scores from the open PGS Catalog "
            "(https://www.pgscatalog.org/). Not medical advice, not diagnosis, "
            "not calibrated absolute risk. Cite each score’s publication; follow "
            "EBI / author license terms."
        ),
        "how_to_read": (
            "Each card is a weighted allele sum for one published score. "
            "Coverage on your chip matters more than the raw number. "
            f"This file is a diverse subset (≤{args.max_variants} variants each, "
            f"up to {args.limit} traits) — not the entire PGS Catalog."
        ),
        "source_note": (
            f"Downloaded {len(scores)} scores (max_variants={args.max_variants}, "
            f"limit={args.limit}); {errors} errors."
        ),
        "scores": scores,
    }
    args.out.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    mb = args.out.stat().st_size / (1024 * 1024)
    print(f"Wrote {args.out} ({len(scores)} scores, {mb:.2f} MiB)", flush=True)
    return 0 if scores else 1


if __name__ == "__main__":
    sys.exit(main())
