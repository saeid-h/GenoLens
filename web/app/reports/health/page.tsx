"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { getHealth } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function HealthPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getHealth(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  return (
    <div className="panel">
      <h1>Health & carrier-style markers</h1>
      <p>
        Condition-linked markers discussed as carrier or risk associations in the
        literature (e.g. hemochromatosis HFE, CFTR-style, sickle HBB). These are
        never a diagnosis or a clinical carrier report — confirm anything
        important with a medical lab.
      </p>
      <Disclaimer text="Never a diagnosis. Exploratory literature-linked markers only." />
      {data && (
        <p className="muted">
          Called {data.markers_called}/{data.markers_total} on this file
        </p>
      )}
      {data && <HitsTable hits={data.hits || []} />}
    </div>
  );
}
