"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { getTraits } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function TraitsPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getTraits(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  return (
    <div className="panel">
      <h1>Traits</h1>
      <p>
        Everyday DNA markers — taste, eye/skin tendencies, earwax, muscle-related
        SNPs, and some research associations. These are interesting genotype facts,
        not medical results.
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
