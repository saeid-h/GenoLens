"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { PredictionCards } from "@/components/PredictionCards";
import { getWellness } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function WellnessPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getWellness(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  const hits = data?.hits || [];
  return (
    <div className="panel">
      <h1>Wellness</h1>
      <p>
        Metabolism-oriented markers — folate, stress chemistry (COMT), alcohol flush enzymes,
        antioxidant research SNPs, and sleep-adjacent CLOCK. Exploratory, not diet advice.
      </p>
      <details className="about-collapse">
        <summary>About this result</summary>
        <Disclaimer text={data?.disclaimer} />
      </details>
      {data && (
        <p className="muted">
          Called {data.markers_called}/{data.markers_total} on this file
        </p>
      )}
      {data && <PredictionCards hits={hits} />}
      {data && (
        <>
          <h2>All markers</h2>
          <HitsTable hits={hits} />
        </>
      )}
    </div>
  );
}
