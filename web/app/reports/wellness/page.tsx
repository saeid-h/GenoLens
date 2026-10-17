"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { getWellness } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function WellnessPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getWellness(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  return (
    <div className="panel">
      <h1>Wellness</h1>
      <p>
        Metabolism-oriented markers — folate processing, stress-chemical breakdown
        (COMT), alcohol flush enzymes, antioxidant/detox research SNPs, and a
        sleep-adjacent body-clock variant. Exploratory lifestyle chemistry, not diet
        or sleep prescriptions.
      </p>
      <Disclaimer text={data?.disclaimer} />
      {data && (
        <p className="muted">
          Called {data.markers_called}/{data.markers_total} on this file
        </p>
      )}
      {data && <HitsTable hits={data.hits || []} />}
    </div>
  );
}
