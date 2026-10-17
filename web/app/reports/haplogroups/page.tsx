"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { getHaplogroups } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function HaplogroupsPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    if (!primaryId) return;
    getHaplogroups(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);

  return (
    <div className="panel">
      <h1>Haplogroups</h1>
      <p>
        Paternal (Y) and maternal (mt) lineage <em>hints</em> from a small open SNP tree.
        23andMe’s paternal haplogroup is usually much more detailed because they score
        thousands of Y markers (including private i-ids). GenoLens will often stop at a
        broader branch such as CT, CF, or P.
      </p>
      <Disclaimer text={data?.disclaimer} />
      {!data ? (
        <p className="muted">Loading…</p>
      ) : (
        <div className="grid">
          {(["Y", "mt"] as const).map((key) => {
            const call = data[key] || {};
            const evidence = (call.evidence || []).filter(
              (e: { match?: boolean; soft_pass?: boolean }) => e.match || e.soft_pass
            );
            return (
              <div className="card" key={key}>
                <h3>{key === "Y" ? "Paternal (Y)" : "Maternal (mt)"}</h3>
                <p style={{ fontFamily: "var(--font-display)", fontSize: "1.6rem", margin: "0.4rem 0" }}>
                  {call.haplogroup || "unresolved"}
                </p>
                <p className="muted">Path: {(call.path || []).join(" → ") || "—"}</p>
                <p className="muted">
                  Markers called {call.markers_called}/{call.markers_tested}
                </p>
                <p>{call.note}</p>
                {evidence.length > 0 && (
                  <table className="data" style={{ marginTop: "0.75rem" }}>
                    <thead>
                      <tr>
                        <th>Branch</th>
                        <th>SNP</th>
                        <th>Your call</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evidence.map((e: any) => (
                        <tr key={`${e.haplogroup}-${e.rsid || e.snp}`}>
                          <td>{e.haplogroup}</td>
                          <td>{e.snp || e.rsid || "—"}</td>
                          <td>{e.genotype || "missing"}</td>
                          <td>
                            {e.match ? "derived match" : e.soft_pass ? "soft-pass (chip gap)" : "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
