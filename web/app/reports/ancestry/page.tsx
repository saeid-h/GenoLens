"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { PercentBars } from "@/components/PercentBars";
import { PieChart } from "@/components/PieChart";
import { getAncestry } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function AncestryPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!primaryId) return;
    getAncestry(primaryId)
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, [primaryId]);

  const regionPct = (data?.region_percentages || data?.percentages || {}) as Record<string, number>;
  const labels = (data?.population_labels || {}) as Record<string, string>;
  const regionItems = Object.entries(regionPct).map(([code, percent]) => ({
    code,
    label: labels[code] || code,
    percent: Number(percent),
  }));
  const topPops = (data?.top_populations || []) as Array<{
    code: string;
    label: string;
    percent: number;
    region?: string;
  }>;

  return (
    <div className="panel">
      <h1>Ancestry Composition</h1>
      <p>
        Affinity to <strong>1000 Genomes reference populations</strong> (open data), then rolled up
        into continental regions. This is <em>not</em> a country or ethnicity estimate — 1000
        Genomes has no dedicated Iranian / Levant / North Africa panels, so West Asian genomes
        often look closest to South Asian (GIH, ITU, PJL) and/or Southern European (TSI, IBS)
        references.
      </p>
      <p>
        <Link href="/catalog/ancestry">Browse the reference catalog →</Link>
      </p>
      <Disclaimer text={String(data?.method_summary || data?.disclaimer || "")} />
      {error && <p className="muted">{error}</p>}
      {data && (
        <>
          <p>
            <strong>Closest region:</strong>{" "}
            <Link href={`/catalog/ancestry/${String(data.superpopulation || "")}`}>
              {String(data.superpopulation_label || data.superpopulation || "—")}
            </Link>{" "}
            <span className="muted">
              ({String(data.method)}; {String(data.markers_used)}/
              {String(data.markers_total || "?")} markers)
            </span>
          </p>
          <h2>Regional affinity</h2>
          <div className="ancestry-viz">
            <PieChart items={regionItems} />
            <div>
              <PercentBars
                items={regionItems.map((i) => ({
                  ...i,
                  label: i.label,
                }))}
              />
              <ul className="catalog-inline">
                {regionItems.map((i) => (
                  <li key={i.code}>
                    <Link href={`/catalog/ancestry/${i.code}`}>{i.label}</Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          {topPops.length > 0 && (
            <>
              <h2>Closest 1000 Genomes populations</h2>
              <p className="muted">
                Fine-scale references used under the hood. Use these to see whether the call is
                Southern European, South Asian, etc. — not a nationality label.
              </p>
              <table className="data">
                <thead>
                  <tr>
                    <th>Population</th>
                    <th>Region</th>
                    <th>Affinity %</th>
                  </tr>
                </thead>
                <tbody>
                  {topPops.map((p) => (
                    <tr key={p.code}>
                      <td>
                        <Link href={`/catalog/ancestry/${p.code}`}>{p.label}</Link>{" "}
                        <span className="muted">({p.code})</span>
                      </td>
                      <td>
                        {p.region ? (
                          <Link href={`/catalog/ancestry/${p.region}`}>{p.region}</Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>{p.percent.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
          {data.note && <p className="muted">{String(data.note)}</p>}
        </>
      )}
    </div>
  );
}
