"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HubIllustration } from "@/components/illustrations";
import { getOverview, REPORTS } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function ReportsHub() {
  const { primaryId } = useSample();
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!primaryId) return;
    getOverview(primaryId).then(setOverview).catch(() => setOverview(null));
  }, [primaryId]);

  return (
    <div>
      <h1 style={{ fontFamily: "var(--font-display)", marginTop: 0 }}>Your reports</h1>
      <Disclaimer text={String(overview?.disclaimer || "")} />
      {overview && (
        <div className="summary">
          <div className="metric">
            <div className="label">SNPs</div>
            <div className="value">{Number(overview.count || 0).toLocaleString()}</div>
          </div>
          <div className="metric">
            <div className="label">Build</div>
            <div className="value">{String(overview.build ?? "—")}</div>
          </div>
          <div className="metric">
            <div className="label">Source</div>
            <div className="value">{String(overview.source ?? "—")}</div>
          </div>
          <div className="metric">
            <div className="label">Sex</div>
            <div className="value">{String(overview.sex ?? "—")}</div>
          </div>
        </div>
      )}
      <div className="grid hub-grid">
        {REPORTS.map((r) => (
          <Link key={r.slug} href={`/reports/${r.slug}`} className="hub-card">
            <div className="hub-card-art">
              <HubIllustration name={r.illustration} />
            </div>
            <div className="hub-card-body">
              <h3>{r.title}</h3>
              <p>{r.blurb}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
