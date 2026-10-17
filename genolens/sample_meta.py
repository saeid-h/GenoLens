"""Optional per-sample metadata (birth year / generation) — gitignored file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from genolens.paths import DATA_DIR

META_PATH = DATA_DIR / "sample_meta.json"


def load_meta(path: Path | None = None) -> dict[str, Any]:
    meta_path = path or META_PATH
    if not meta_path.is_file():
        return {"samples": {}}
    with meta_path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if "samples" not in data:
        data = {"samples": data}
    return data


def save_meta(data: dict[str, Any], path: Path | None = None) -> Path:
    meta_path = path or META_PATH
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return meta_path


def get_sample_meta(sample_id: str, path: Path | None = None) -> dict[str, Any]:
    return dict(load_meta(path).get("samples", {}).get(sample_id, {}))


def upsert_sample_meta(sample_id: str, fields: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    data = load_meta(path)
    samples = data.setdefault("samples", {})
    cur = dict(samples.get(sample_id, {}))
    for key, value in fields.items():
        if value is None or value == "":
            cur.pop(key, None)
        else:
            cur[key] = value
    samples[sample_id] = cur
    save_meta(data, path)
    return cur
