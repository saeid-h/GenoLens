"use client";

import Link from "next/link";
import { useSample } from "@/lib/sample";

export default function HomePage() {
  const { primaryId, samples } = useSample();
  const primary = samples.find((s) => s.id === primaryId);

  return (
    <section className="hero">
      <h1>GenoLens</h1>
      <p>
        Private DNA reports on this machine
        {primary ? ` for ${primary.label}` : ""}. Nothing is uploaded. Explore ancestry,
        traits, relatives, and ancient affinity with open data.
      </p>
      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <Link className="cta" href="/reports">
          View reports
        </Link>
        <Link className="cta secondary" href="/settings/samples">
          Manage samples
        </Link>
      </div>
    </section>
  );
}
