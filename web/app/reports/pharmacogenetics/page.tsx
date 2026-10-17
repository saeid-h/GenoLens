"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { PredictionCards } from "@/components/PredictionCards";
import { getPharma } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function PharmaPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getPharma(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  const hits = data?.hits || [];
  return (
    <div className="panel">
      <h1>Pharmacogenetics</h1>
      <p>
        Drug–gene research markers (CYP enzymes, statin transport, TPMT, opioid receptor, caffeine
        CYP1A2). A single SNP is only a hint — never start, stop, or change a medicine based on
        GenoLens alone.
      </p>
      <details className="about-collapse">
        <summary>About this result</summary>
        <Disclaimer text="Exploratory drug-gene markers only. Not prescribing guidance." />
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
