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
      <Disclaimer />
      {!data ? (
        <p className="muted">Loading…</p>
      ) : (
        <div className="grid">
          {(["Y", "mt"] as const).map((key) => {
            const call = data[key] || {};
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
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
