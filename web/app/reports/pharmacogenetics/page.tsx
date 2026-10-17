"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HitsTable } from "@/components/HitsTable";
import { getPharma } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function PharmaPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getPharma(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);
  return (
    <div className="panel">
      <h1>Pharmacogenetics</h1>
      <Disclaimer text="Exploratory drug-gene markers only. Not prescribing guidance." />
      {data && <HitsTable hits={data.hits || []} />}
    </div>
  );
}
