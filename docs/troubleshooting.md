# Troubleshooting

## Browser shows `404` / `{"detail":"Not Found"}`

**Cause:** You opened the **API** port (`http://127.0.0.1:8000/`) instead of the
**UI**, or the Next.js app is not running.

GenoLens needs **two** processes:

```bash
# Terminal 1 — API
uvicorn api.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — UI
cd web && npm run dev
```

Then open **http://localhost:3000** (not `:8000`).

- API OpenAPI UI: http://127.0.0.1:8000/docs
- API health: http://127.0.0.1:8000/api/health

---

## UI shows “API offline”

**Cause:** Next.js cannot reach FastAPI.

**Checks:**

```bash
curl -s http://127.0.0.1:8000/api/health
```

- Start uvicorn on `127.0.0.1:8000`.
- Confirm nothing else bound the port.
- If using a custom base URL, set `NEXT_PUBLIC_API_BASE` consistently.

---

## Empty sample list

**Cause:** No supported files under `data/`, or files only under `data/reference/`.

**Fix:** Place genotype files directly in `data/` with a supported extension
(`.txt`, `.csv`, `.tsv`, `.vcf`, `.vcf.gz`, `.zip`).

---

## Ancestry looks weak / uninformative

AIM panels are sparse relative to commercial ethnicity products. GenoLens reports
**continental affinity %**, not country ethnicity. More markers / denser open refs
improve resolution later; they still will not match consumer marketing claims.

---

## Haplogroup `unresolved` (mt)

Should be rare after the soft-pass + MT position marker fix. If it still appears:

1. Confirm the file loads (`/overview` SNP count > 0).
2. Inspect `markers_called` on the haplogroups payload.
3. Chip may lack all defining alleles in `haplogroups.json` — expand the tree with
   markers present on *your* chip (verify rsIDs/positions locally).

---

## Relatives: everyone “no relationship”

Common causes:

- Files are not overlapping enough (different chips / too few shared SNPs).
- `lineage` genetic maps not downloaded yet (first run may need network once for maps under `resources/`).
- Comparing the wrong primary/candidates.

Inspect pair `error` fields in the compare API response.

---

## Pedigree puts relatives in the wrong generation

1. Enter **birth years** in Settings.
2. Prefer pairs with measured **IBD2** (siblings vs parent–child).
3. Accept undirected edges when ambiguous — label manually rather than forcing a tree.

---

## Ancient hub is demo-only

Without a prepared AADR panel, GenoLens falls back to a demo panel. Prepare a real
panel under `data/reference/panel/` — see [Open reference data](reference-data.md).

---

## Changed a genome file but API returns old results

In-process `lru_cache` keys on path string. Restart uvicorn after replacing a file
in place.

---

## pytest failures involving real genomes

Some tests skip or adapt when private `data/genome_*.txt` files are absent. CI /
fresh clones without genomes should still pass synthetic tests. Do not commit
private files to “make tests green.”

---

## npm / Next build warnings

Autoprefixer or dependency audit warnings may appear; they are not necessarily
blockers. Prefer `npm run build` success and `npx tsc --noEmit` clean.

---

## Accidental staging of genomes

```bash
git status
git restore --staged data/...
```

Confirm `.gitignore` still lists `data/*.txt`, `data/reference/`, `data/sample_meta.json`.

## Related docs

- [Getting started](getting-started.md)
- [Relatives and pedigree](relatives-and-pedigree.md)
- [Development](development.md)
