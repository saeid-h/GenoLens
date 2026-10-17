"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { getPrs } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function PrsPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getPrs(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);

  return (
    <div className="panel">
      <h1>Polygenic scores</h1>
      <Disclaimer text={data?.disclaimer} />
      <p className="muted">{data?.pgs_catalog_hint}</p>
      <table className="data">
        <thead>
          <tr>
            <th>Trait</th>
            <th>Raw score</th>
            <th>Variants used</th>
            <th>Missing</th>
            <th>Citation</th>
          </tr>
        </thead>
        <tbody>
          {(data?.scores || []).map((s: any) => (
            <tr key={s.id}>
              <td>{s.trait}</td>
              <td>{Number(s.raw_score).toFixed(4)}</td>
              <td>{s.variants_used}</td>
              <td>{s.variants_missing}</td>
              <td>{s.citation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
