"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { PhenotypeSketch } from "@/components/PhenotypeSketch";
import { PredictionCards } from "@/components/PredictionCards";
import { getTraits } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function TraitsPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getTraits(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  const hits = data?.hits || [];
  return (
    <div className="panel">
      <h1>Traits</h1>
      <p>
        Everyday DNA markers — taste, eye/skin tendencies, earwax, muscle-related SNPs, and some
        research associations. Predictions first; details below.
      </p>
      <details className="about-collapse">
        <summary>About this result</summary>
        <Disclaimer text={data?.disclaimer} />
        <p className="muted">
          These are interesting genotype facts, not medical results. Microarray chips cover a tiny
          fraction of the genome.
        </p>
      </details>
      {data && (
        <p className="muted">
          Called {data.markers_called}/{data.markers_total} on this file
        </p>
      )}
      {data && <PhenotypeSketch hits={hits} />}
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
