"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { getArchaic } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function ArchaicPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getArchaic(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);

  return (
    <div className="panel">
      <h1>Archaic affinity</h1>
      <Disclaimer text={data?.disclaimer} />
      {data && (
        <div className="summary">
          <div className="metric">
            <div className="label">Markers present</div>
            <div className="value">
              {data.markers_present}/{data.markers_tested}
            </div>
          </div>
          <div className="metric">
            <div className="label">Archaic allele hits</div>
            <div className="value">{data.archaic_allele_hits}</div>
          </div>
          <div className="metric">
            <div className="label">Fraction of present</div>
            <div className="value">{(100 * Number(data.fraction_of_present || 0)).toFixed(1)}%</div>
          </div>
        </div>
      )}
      <table className="data">
        <thead>
          <tr>
            <th>rsID</th>
            <th>Genotype</th>
            <th>Archaic allele</th>
            <th>Hit</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody>
          {(data?.hits || []).map((h: any) => (
            <tr key={h.rsid}>
              <td>{h.rsid}</td>
              <td>{h.genotype || "—"}</td>
              <td>{h.archaic_allele}</td>
              <td>{h.carries_archaic ? "yes" : "no"}</td>
              <td>{h.note}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
