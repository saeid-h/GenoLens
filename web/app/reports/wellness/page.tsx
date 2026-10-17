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
      <Disclaimer text={data?.disclaimer} />
      {data && <HitsTable hits={data.hits || []} />}
    </div>
  );
}
