#!/usr/bin/env python3
"""Build a denser 1000 Genomes population-level ancestry panel via Ensembl REST.

Writes ``genolens/data/aim_panel.json`` (replaces the shallow 5-superpop panel).
Requires network once; ships the result for offline analysis.
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "genolens" / "data" / "aim_panel.json"

# 1000 Genomes Phase 3 analysis populations (not only 5 supers).
POPS = [
    "ACB", "ASW", "BEB", "CDX", "CEU", "CHB", "CHS", "CLM", "ESN", "FIN",
    "GBR", "GIH", "GWD", "IBS", "ITU", "JPT", "KHV", "LWK", "MSL", "MXL",
    "PEL", "PJL", "PUR", "STU", "TSI", "YRI",
]

POP_LABELS = {
    "ACB": "African Caribbean (Barbados)",
    "ASW": "African Ancestry (SW US)",
    "BEB": "Bengali (Bangladesh)",
    "CDX": "Chinese Dai (China)",
    "CEU": "Utah European (CEPH)",
    "CHB": "Han Chinese (Beijing)",
    "CHS": "Southern Han Chinese",
    "CLM": "Colombian (Medellín)",
    "ESN": "Esan (Nigeria)",
    "FIN": "Finnish",
    "GBR": "British (England/Scotland)",
    "GIH": "Gujarati Indian (Houston)",
    "GWD": "Gambian (Western Divisions)",
    "IBS": "Iberian (Spain)",
    "ITU": "Indian Telugu (UK)",
    "JPT": "Japanese (Tokyo)",
    "KHV": "Kinh Vietnamese (Ho Chi Minh)",
    "LWK": "Luhya (Kenya)",
    "MSL": "Mende (Sierra Leone)",
    "MXL": "Mexican Ancestry (LA)",
    "PEL": "Peruvian (Lima)",
    "PJL": "Punjabi (Lahore)",
    "PUR": "Puerto Rican",
    "STU": "Sri Lankan Tamil (UK)",
    "TSI": "Toscani (Italy)",
    "YRI": "Yoruba (Nigeria)",
}

# Map analysis pops → regions GenoLens shows as secondary bars.
REGION_OF = {
    "YRI": "AFR", "LWK": "AFR", "GWD": "AFR", "MSL": "AFR", "ESN": "AFR",
    "ACB": "AFR", "ASW": "AFR",
    "CEU": "EUR", "GBR": "EUR", "FIN": "EUR", "IBS": "EUR", "TSI": "EUR",
    "CHB": "EAS", "JPT": "EAS", "CHS": "EAS", "CDX": "EAS", "KHV": "EAS",
    "GIH": "SAS", "PJL": "SAS", "BEB": "SAS", "STU": "SAS", "ITU": "SAS",
    "MXL": "AMR", "PUR": "AMR", "CLM": "AMR", "PEL": "AMR",
}

REGION_LABELS = {
    "AFR": "African",
    "EUR": "European",
    "EAS": "East Asian",
    "SAS": "South Asian",
    "AMR": "Admixed American",
}

# Curated ancestry-informative rsIDs (Kidd AISNP + common GWAS AIMs + prior panel).
# Only markers that return 1000G freqs will be kept.
RSIDS = [
    # prior panel
    "rs3737576", "rs7554936", "rs2814778", "rs10079352", "rs1871534",
    "rs1834640", "rs2675345", "rs10496971", "rs3827760", "rs1426654",
    "rs16891982", "rs885479", "rs12913832", "rs1805007", "rs1800407",
    "rs12896399", "rs1229984", "rs3811801", "rs671", "rs17822931",
    "rs4918664", "rs4833103", "rs1877452", "rs3793451", "rs260690",
    "rs2196051", "rs2330442", "rs2593595", "rs1572018", "rs7324938",
    "rs9522149",
    # Kidd / forensic AISNP-style markers commonly on DTC chips
    "rs10497191", "rs12498138", "rs1410059", "rs1462906", "rs1478829",
    "rs1498444", "rs1554472", "rs17642714", "rs182549", "rs192655",
    "rs1991961", "rs200354", "rs2042762", "rs2075091", "rs217727",
    "rs239031", "rs2416791", "rs2470102", "rs2593595", "rs2814778",
    "rs310644", "rs3784230", "rs3827760", "rs3907047", "rs4460045",
    "rs4593064", "rs4784809", "rs4833103", "rs4918664", "rs6548616",
    "rs7226659", "rs7263910", "rs731257", "rs7324938", "rs735480",
    "rs7657799", "rs772262", "rs798443", "rs7997709", "rs8035124",
    "rs870347", "rs917115", "rs9522149", "rs9530435", "rs9591325",
    "rs9865481", "rs11652805", "rs12439433", "rs12629908", "rs12913832",
    "rs13213338", "rs1335873", "rs13400937", "rs1362787", "rs1426654",
    "rs1461222", "rs1478829", "rs1498444", "rs1513181", "rs1528460",
    "rs1554472", "rs1572018", "rs16891982", "rs17642714", "rs1834640",
    "rs1871534", "rs1877452", "rs192655", "rs1991961", "rs200354",
    "rs2042762", "rs2075091", "rs217727", "rs2196051", "rs2330442",
    "rs239031", "rs2416791", "rs2470102", "rs260690", "rs2675345",
    "rs310644", "rs3784230", "rs3793451", "rs3811801", "rs3907047",
    "rs4460045", "rs4593064", "rs4784809", "rs6548616", "rs7226659",
    "rs7263910", "rs731257", "rs735480", "rs7657799", "rs772262",
    "rs798443", "rs7997709", "rs8035124", "rs870347", "rs917115",
    "rs9530435", "rs9591325", "rs9865481", "rs10079352", "rs10496971",
    "rs11652805", "rs12439433", "rs12629908", "rs13213338", "rs1335873",
    "rs13400937", "rs1362787", "rs1461222", "rs1513181", "rs1528460",
    # pigmentation / classic continental AIMs
    "rs1426654", "rs16891982", "rs12913832", "rs885479", "rs1805007",
    "rs1800407", "rs12896399", "rs1126809", "rs1667394", "rs1408799",
    "rs1393350", "rs683", "rs6059655", "rs12203592", "rs1540771",
    "rs2378249", "rs4911414", "rs1015362", "rs28777", "rs1834640",
    "rs642742", "rs1042602", "rs4918664", "rs3827760", "rs17822931",
    "rs2814778", "rs182549", "rs4988235", "rs182549", "rs3737576",
    "rs7554936", "rs1871534", "rs2675345", "rs10496971", "rs4833103",
    "rs3793451", "rs260690", "rs2196051", "rs2330442", "rs1572018",
    "rs7324938", "rs9522149", "rs3811801", "rs671", "rs1229984",
]


def _ensembl_variation(rsid: str) -> dict:
    url = f"https://rest.ensembl.org/variation/human/{rsid}?pops=1"
    req = urllib.request.Request(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        return json.loads(resp.read().decode())


def _pick_allele_and_freqs(payload: dict) -> tuple[str, dict[str, float]] | None:
    """Choose the non-reference-ish allele with the most population spread for AIMs."""
    pops = payload.get("populations") or []
    by_pop: dict[str, dict[str, float]] = {p: {} for p in POPS}
    for row in pops:
        name = str(row.get("population") or "")
        if not name.startswith("1000GENOMES:phase_3:"):
            continue
        code = name.rsplit(":", 1)[-1]
        if code not in by_pop:
            continue
        allele = str(row.get("allele") or "").upper()
        if allele not in {"A", "C", "G", "T"}:
            continue
        by_pop[code][allele] = float(row.get("frequency") or 0.0)

    # Need coverage across most pops
    covered = [p for p, alleles in by_pop.items() if alleles]
    if len(covered) < 18:
        return None

    alleles = sorted({a for freqs in by_pop.values() for a in freqs})
    if len(alleles) < 2:
        return None

    # Prefer allele with high between-pop variance (more ancestry-informative).
    best_allele = None
    best_var = -1.0
    for allele in alleles:
        vals = []
        for pop in POPS:
            vals.append(by_pop[pop].get(allele, 0.0))
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        if var > best_var:
            best_var = var
            best_allele = allele
    if not best_allele or best_var < 0.002:
        return None

    freqs = {}
    for pop in POPS:
        freqs[pop] = float(by_pop[pop].get(best_allele, 0.0))
    return best_allele, freqs


def main() -> None:
    markers = []
    seen: set[str] = set()
    for rsid in RSIDS:
        if rsid in seen:
            continue
        seen.add(rsid)
        try:
            payload = _ensembl_variation(rsid)
            picked = _pick_allele_and_freqs(payload)
            time.sleep(0.12)  # be polite to Ensembl
        except Exception as exc:  # noqa: BLE001
            print(f"skip {rsid}: {exc}")
            continue
        if not picked:
            print(f"skip {rsid}: insufficient 1000G coverage / variance")
            continue
        allele, freqs = picked
        markers.append({"rsid": rsid, "allele": allele, "freq": freqs})
        print(f"ok {rsid} allele={allele} n_markers={len(markers)}")

    panel = {
        "disclaimer": (
            "Exploratory affinity to 1000 Genomes Phase 3 reference populations "
            "(Ensembl allele frequencies). Not ethnicity, nationality, or tribal identity. "
            "1000 Genomes has no dedicated Iranian/Levant/North-Africa panels — West Asian "
            "genomes often look closest to South Asian (GIH/ITU/PJL) and/or Southern European "
            "(TSI/IBS) references."
        ),
        "method": "aim_pop_likelihood",
        "method_summary": (
            "Bars are normalized genotype likelihoods against 1000 Genomes analysis "
            "populations, then rolled up into continental regions. More markers than the "
            "old 31-SNP panel, but still not a consumer ethnicity estimate."
        ),
        "source": "Ensembl REST variation populations · 1000GENOMES:phase_3",
        "populations": POPS,
        "population_labels": POP_LABELS,
        "regions": list(REGION_LABELS.keys()),
        "region_labels": REGION_LABELS,
        "region_of": REGION_OF,
        "superpopulations": list(REGION_LABELS.keys()),
        "labels": REGION_LABELS,
        "markers": markers,
    }
    OUT.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} with {len(markers)} markers")


if __name__ == "__main__":
    main()
