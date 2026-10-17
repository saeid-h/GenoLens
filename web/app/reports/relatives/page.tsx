"use client";

import { useMemo, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { PedigreeView } from "@/components/PedigreeView";
import { compare, familyTree } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function RelativesPage() {
  const { primaryId, samples } = useSample();
  const [selected, setSelected] = useState<string[]>([]);
  const [pairs, setPairs] = useState<any[]>([]);
  const [pedigree, setPedigree] = useState<any | null>(null);
  const [birthYearsUsed, setBirthYearsUsed] = useState<Record<string, number | null>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      const cmp = await compare(primaryId, selected);
      setPairs((cmp.pairs as any[]) || []);
      const tree = await familyTree(primaryId, selected);
      setPedigree(tree.pedigree || null);
      setBirthYearsUsed((tree.birth_years_used as Record<string, number | null>) || {});
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h1>DNA Relatives</h1>
      <p>
        Pick candidates, then run compare. Birth years from{" "}
        <a href="/settings/samples">Settings → Samples &amp; ages</a> are applied when you
        run — save ages first, then click Compare again to refresh the tree.
      </p>
      <Disclaimer text="We never auto-matrix every file in data/. Shared cM alone cannot tell parent from child; ages and IBD2 orient the tree." />
      <div className="controls">
        <div style={{ flex: 1 }}>
          <div className="muted" style={{ marginBottom: "0.4rem" }}>
            Candidates{" "}
            <button type="button" className="linkish" onClick={selectAll}>
              Select all
            </button>
          </div>
          <div className="candidate-list">
            {candidates.map((s) => {
              const year = (s.meta as { birth_year?: number } | undefined)?.birth_year;
              return (
                <label key={s.id}>
                  <input
                    type="checkbox"
                    checked={selected.includes(s.id)}
                    onChange={() => toggle(s.id)}
                  />{" "}
                  {s.label}
                  {year != null ? <span className="muted"> (b. {year})</span> : (
                    <span className="muted"> (no birth year)</span>
                  )}
                </label>
              );
            })}
          </div>
        </div>
        <button className="cta" disabled={busy || selected.length === 0} onClick={run}>
          {busy ? "Comparing… (may take a minute)" : "Compare selected"}
        </button>
      </div>
      {error && <p className="muted">{error}</p>}
      {!pedigree && !busy && (
        <p className="muted">
          No tree yet — select at least one candidate and click Compare selected. The graph
          appears below the shared-DNA table.
        </p>
      )}
      {pairs.length > 0 && (
        <>
          <h2>Shared DNA vs primary</h2>
          <table className="data">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Shared cM</th>
                <th>IBD2 cM</th>
                <th>Segments</th>
                <th>Estimate</th>
              </tr>
            </thead>
            <tbody>
              {pairs.map((p) => {
                const primaryLabel = samples.find((s) => s.id === primaryId)?.label;
                const other =
                  p.sample_b === primaryLabel ? p.sample_a : p.sample_a === primaryLabel ? p.sample_b : p.sample_b;
                return (
                  <tr key={`${p.sample_a}-${p.sample_b}`}>
                    <td>{other}</td>
                    <td>{Number(p.shared_cm).toFixed(1)}</td>
                    <td>{Number(p.ibd2_cm || 0).toFixed(1)}</td>
                    <td>{p.shared_segments}</td>
                    <td>{p.relationship || p.error || "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}
      {pedigree && (
        <>
          <h2>Family tree (by generation)</h2>
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
          />
        </>
      )}
    </div>
  );
}
