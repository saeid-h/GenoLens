"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { PercentBars } from "@/components/PercentBars";
import { getAncestry } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function AncestryPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!primaryId) return;
    getAncestry(primaryId)
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, [primaryId]);

  const percentages = (data?.percentages || {}) as Record<string, number>;
  const labels = (data?.population_labels || {}) as Record<string, string>;
  const items = Object.entries(percentages).map(([code, percent]) => ({
    code,
    label: labels[code] || code,
    percent: Number(percent),
  }));

  return (
    <div className="panel">
      <h1>Ancestry Composition</h1>
      <Disclaimer text={String(data?.method_summary || data?.disclaimer || "")} />
      {error && <p className="muted">{error}</p>}
      {data && (
        <>
          <p>
            <strong>Call:</strong> {String(data.superpopulation_label || data.superpopulation || "—")}{" "}
            <span className="muted">({String(data.method)})</span>
          </p>
          <PercentBars items={items} />
        </>
      )}
    </div>
  );
}
