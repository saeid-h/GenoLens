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
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const candidates = useMemo(
    () => samples.filter((s) => s.id !== primaryId),
    [samples, primaryId]
  );

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const run = async () => {
    if (!primaryId || selected.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      const cmp = await compare(primaryId, selected);
      setPairs((cmp.pairs as any[]) || []);
      const tree = await familyTree(primaryId, selected);
      setPedigree(tree.pedigree || null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h1>DNA Relatives</h1>
      <Disclaimer text="Select candidates to compare with the primary sample. We never auto-matrix every file in data/." />
      <div className="controls">
        <div style={{ flex: 1 }}>
          <div className="muted" style={{ marginBottom: "0.4rem" }}>
            Candidates
          </div>
          <div className="candidate-list">
            {candidates.map((s) => (
              <label key={s.id}>
                <input
                  type="checkbox"
                  checked={selected.includes(s.id)}
                  onChange={() => toggle(s.id)}
                />{" "}
                {s.label}
              </label>
            ))}
          </div>
        </div>
        <button className="cta" disabled={busy || selected.length === 0} onClick={run}>
          {busy ? "Comparing…" : "Compare selected"}
        </button>
      </div>
      {error && <p className="muted">{error}</p>}
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
              {pairs.map((p) => (
                <tr key={`${p.sample_a}-${p.sample_b}`}>
                  <td>{p.sample_b === samples.find((s) => s.id === primaryId)?.label ? p.sample_a : p.sample_b}</td>
                  <td>{Number(p.shared_cm).toFixed(1)}</td>
                  <td>{Number(p.ibd2_cm || 0).toFixed(1)}</td>
                  <td>{p.shared_segments}</td>
                  <td>{p.relationship || p.error || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      {pedigree && (
        <>
          <h2>Family tree (directional)</h2>
          <PedigreeView nodes={pedigree.nodes || []} edges={pedigree.edges || []} notes={pedigree.notes} />
        </>
      )}
    </div>
  );
}
