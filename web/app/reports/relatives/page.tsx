"use client";

import { useMemo, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { IllEmptyRelatives } from "@/components/illustrations";
import { PedigreeView } from "@/components/PedigreeView";
import { familyTree } from "@/lib/api";
import { useSample } from "@/lib/sample";

type Pair = {
  sample_a: string;
  sample_b: string;
  shared_cm: number;
  ibd2_cm?: number;
  shared_segments?: number;
  relationship?: string;
  error?: string;
};

function pairKey(p: Pair) {
  return [p.sample_a, p.sample_b].sort().join("::");
}

function otherLabel(p: Pair, primaryLabel: string | undefined) {
  if (!primaryLabel) return p.sample_b;
  if (p.sample_a === primaryLabel) return p.sample_b;
  if (p.sample_b === primaryLabel) return p.sample_a;
  return `${p.sample_a} ↔ ${p.sample_b}`;
}

function involvesPrimary(p: Pair, primaryLabel: string | undefined) {
  if (!primaryLabel) return true;
  return p.sample_a === primaryLabel || p.sample_b === primaryLabel;
}

export default function RelativesPage() {
  const { primaryId, samples } = useSample();
  const [selected, setSelected] = useState<string[]>([]);
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [pedigree, setPedigree] = useState<any | null>(null);
  const [birthYearsUsed, setBirthYearsUsed] = useState<Record<string, number | null>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const primaryLabel = samples.find((s) => s.id === primaryId)?.label;

  const candidates = useMemo(
    () => samples.filter((s) => s.id !== primaryId),
    [samples, primaryId]
  );

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const selectAll = () => setSelected(candidates.map((c) => c.id));

  const run = async () => {
    if (!primaryId || selected.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      // family-tree already includes primary×candidates and candidate×candidate (≤8 people).
      // Skip a separate /api/compare so we do not double the runtime and hit proxy timeouts.
      const tree = await familyTree(primaryId, selected);
      const treePairs = ((tree.pairs as Pair[]) || []) as Pair[];
      setPairs([...treePairs].sort((a, b) => Number(b.shared_cm) - Number(a.shared_cm)));
      setPedigree(tree.pedigree || null);
      setBirthYearsUsed((tree.birth_years_used as Record<string, number | null>) || {});
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const withYou = pairs.filter((p) => involvesPrimary(p, primaryLabel));
  const amongRelatives = pairs.filter((p) => !involvesPrimary(p, primaryLabel));

  return (
    <div className="panel">
      <h1>DNA Relatives</h1>
      <p>
        Pick candidates, then run compare. Birth years from{" "}
        <a href="/settings/samples">Settings → Samples &amp; ages</a> are applied when you run —
        save ages first, then click Compare again to refresh the tree.
      </p>
      <p className="muted">
        When you select mother and grandmother (or any 3–8 people including you), we also compare
        them to each other to orient the tree.
      </p>
      <Disclaimer text="We never auto-matrix every file in data/. Shared cM alone cannot tell parent from child; ages and IBD2 orient the tree." />

      <div className="relatives-sticky">
        <div className="candidate-chips">
          {candidates.map((s) => {
            const year = (s.meta as { birth_year?: number } | undefined)?.birth_year;
            const on = selected.includes(s.id);
            return (
              <button
                key={s.id}
                type="button"
                className={`chip ${on ? "chip-on" : ""}`}
                onClick={() => toggle(s.id)}
              >
                {s.label}
                {year != null ? <span className="chip-badge">b. {year}</span> : null}
              </button>
            );
          })}
        </div>
        <div className="relatives-actions">
          <button type="button" className="linkish" onClick={selectAll}>
            Select all
          </button>
          <button className="cta" disabled={busy || selected.length === 0} onClick={run}>
            {busy ? "Comparing… (often 1–2 minutes for several genomes)" : "Compare selected"}
          </button>
        </div>
      </div>

      {error && <p className="muted">{error}</p>}

      {!pedigree && !busy && pairs.length === 0 && (
        <div className="empty-relatives">
          <IllEmptyRelatives />
        </div>
      )}

      {pedigree && (
        <>
          <h2>Family tree</h2>
          {Object.keys(birthYearsUsed).length > 0 && (
            <p className="muted">
              Birth years used:{" "}
              {Object.entries(birthYearsUsed)
                .map(([k, v]) => `${k}: ${v ?? "—"}`)
                .join(" · ")}
            </p>
          )}
          <PedigreeView
            nodes={pedigree.nodes || []}
            edges={pedigree.edges || []}
            notes={pedigree.notes}
            birthYears={birthYearsUsed}
            asciiTree={pedigree.ascii_tree}
            detailsCollapsed
          />
        </>
      )}

      {withYou.length > 0 && (
        <>
          <h2>With you</h2>
          <div className="relationship-cards">
            {withYou.map((p) => (
              <div className="relationship-card" key={pairKey(p)}>
                <div className="relationship-who">{otherLabel(p, primaryLabel)}</div>
                <div className="relationship-label">{p.relationship || p.error || "—"}</div>
                <div className="muted">
                  {Number(p.shared_cm).toFixed(0)} cM · IBD2 {Number(p.ibd2_cm || 0).toFixed(0)} cM ·{" "}
                  {p.shared_segments ?? "—"} segments
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {amongRelatives.length > 0 && (
        <>
          <h2>Among selected relatives</h2>
          <p className="muted">
            Candidate × candidate pairs (for example mother × grandmother) used to triangulate the
            tree.
          </p>
          <div className="relationship-cards">
            {amongRelatives.map((p) => (
              <div className="relationship-card" key={pairKey(p)}>
                <div className="relationship-who">
                  {p.sample_a} ↔ {p.sample_b}
                </div>
                <div className="relationship-label">{p.relationship || p.error || "—"}</div>
                <div className="muted">
                  {Number(p.shared_cm).toFixed(0)} cM · IBD2 {Number(p.ibd2_cm || 0).toFixed(0)} cM ·{" "}
                  {p.shared_segments ?? "—"} segments
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
