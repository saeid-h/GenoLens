"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { getAncient } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function AncientPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getAncient(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);

  const individuals = data?.ranked?.individuals || [];
  const groups = data?.ranked?.groups || [];

  return (
    <div className="panel">
      <h1>Ancient affinity</h1>
      <Disclaimer />
      {data?.ranked?.is_demo && (
        <p className="muted">Using synthetic demo panel — download AADR into data/reference/ for real matches.</p>
      )}
      <h2>Closest individuals</h2>
      <table className="data">
        <thead>
          <tr>
            <th>ID</th>
            <th>Group</th>
            <th>Country</th>
            <th>Distance</th>
            <th>SNPs</th>
          </tr>
        </thead>
        <tbody>
          {individuals.map((m: any) => (
            <tr key={m.genetic_id}>
              <td>{m.genetic_id}</td>
              <td>{m.group}</td>
              <td>{m.country}</td>
              <td>{Number(m.distance).toFixed(4)}</td>
              <td>{m.n_snps}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Closest groups</h2>
      <table className="data">
        <thead>
          <tr>
            <th>Group</th>
            <th>Mean distance</th>
            <th>n</th>
          </tr>
        </thead>
        <tbody>
          {groups.map((g: any) => (
            <tr key={g.group}>
              <td>{g.group}</td>
              <td>{Number(g.mean_distance).toFixed(4)}</td>
              <td>{g.n_individuals}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
