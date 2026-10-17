#!/usr/bin/env python3
"""Download a chip-friendly PGS Catalog subset into data/reference/prs/catalog.json.

Does **not** upload genomes. Does **not** download the entire catalog.

Default (best judgment): curated list of published scores with ≤150 variants
(cancers, lipids, diabetes, Alzheimer, BMI, asthma, etc.).

Example:
  .venv/bin/python scripts/download_pgs_catalog.py
  .venv/bin/python scripts/download_pgs_catalog.py --max-variants 100
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "data" / "reference" / "prs" / "catalog.json"

# Recognizable traits / diseases with modest SNP panels (filtered again by size).
CURATED_IDS = [
    "PGS000001",
    "PGS000021",
    "PGS000025",
    "PGS000026",
    "PGS000028",
    "PGS000029",
    "PGS000030",
    "PGS000031",
    "PGS000032",
    "PGS000033",
    "PGS000034",
    "PGS000037",
    "PGS000038",
    "PGS000044",
    "PGS000045",
    "PGS000046",
    "PGS000047",
    "PGS000048",
    "PGS000049",
    "PGS000050",
    "PGS000055",
    "PGS000057",
    "PGS000059",
    "PGS000060",
    "PGS000061",
    "PGS000062",
    "PGS000063",
    "PGS000064",
    "PGS000065",
    "PGS000066",
    "PGS000067",
    "PGS000068",
    "PGS000069",
    "PGS000070",
    "PGS000071",
    "PGS000073",
    "PGS000074",
    "PGS000075",
    "PGS000076",
    "PGS000077",
    "PGS000078",
    "PGS000079",
    "PGS000080",
    "PGS000081",
    "PGS000082",
    "PGS000083",
    "PGS000086",
    "PGS000087",
    "PGS000118",
    "PGS000334",
    "PGS000730",
    "PGS000731",
    "PGS000732",
    "PGS000733",
    "PGS000848",
    "PGS000858",
    "PGS001349",
    "PGS001353",
    "PGS002272",
    "PGS005249",
]


def _fetch(url: str, timeout: int = 90, retries: int = 6) -> bytes:
    last: Exception | None = None
    for i in range(retries):
        try:
            req = Request(
                url,
                headers={"User-Agent": "GenoLens-local/0.0.0 (research; no genome upload)"},
            )
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            time.sleep(1.5 * (i + 1))
    assert last is not None
    raise last


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
        if not rsid.startswith("rs"):
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


def download_one(pgs_id: str, max_variants: int) -> dict[str, Any] | None:
    meta = json.loads(_fetch(f"https://www.pgscatalog.org/rest/score/{pgs_id}").decode())
    n = meta.get("variants_number") or 0
    if n <= 0 or n > max_variants:
        print(f"  skip {pgs_id}: variants_number={n}", flush=True)
        return None
    url = meta.get("ftp_scoring_file")
    if not url:
        return None
    variants = parse_scoring_file(_fetch(url))
    if not variants:
        print(f"  skip {pgs_id}: no rsID rows", flush=True)
        return None
    trait = meta.get("trait_reported") or pgs_id
    return {
        "id": pgs_id,
        "trait": trait,
        "trait_plain": trait,
        "what_it_is": (
            f"Open PGS Catalog score {pgs_id} ({meta.get('name') or ''}). "
            f"Weighted allele sum over {len(variants)} rsID variants."
        ),
        "what_it_is_not": (
            "Not a diagnosis, not calibrated clinical risk, and not a body measurement. "
            "Ancestry of the source GWAS may not match yours."
        ),
        "citation": citation_from_meta(meta),
        "variants_number_catalog": n,
        "variants": variants,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--max-variants", type=int, default=150)
    ap.add_argument("--ids", nargs="*", default=None, help="Override curated PGS ids")
    ap.add_argument("--sleep", type=float, default=0.25)
    args = ap.parse_args()

    ids = args.ids or CURATED_IDS
    print(f"Downloading curated PGS subset ({len(ids)} candidates, ≤{args.max_variants} variants)…", flush=True)
    scores: list[dict[str, Any]] = []
    errors = 0
    for pgs_id in ids:
        try:
            row = download_one(pgs_id, args.max_variants)
            if row:
                scores.append(row)
                print(f"  [{len(scores)}] {row['id']} · {row['trait'][:55]} · {len(row['variants'])} rsIDs", flush=True)
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
            "This file is a curated chip-friendly subset — not the entire PGS Catalog."
        ),
        "source_note": f"Curated download of {len(scores)} scores (≤{args.max_variants} variants); {errors} errors.",
        "scores": scores,
    }
    args.out.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    mb = args.out.stat().st_size / (1024 * 1024)
    print(f"Wrote {args.out} ({len(scores)} scores, {mb:.2f} MiB)", flush=True)
    return 0 if scores else 1


if __name__ == "__main__":
    sys.exit(main())
