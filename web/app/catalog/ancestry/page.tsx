import Link from "next/link";
import { catalogPopulations, catalogRegions } from "@/lib/ancestryCatalog";

export default function AncestryCatalogIndex() {
  const regions = catalogRegions();
  const pops = catalogPopulations();
  return (
    <div className="panel">
      <h1>Ancestry reference catalog</h1>
      <p>
        Short blurbs for the <strong>1000 Genomes</strong> regions and populations GenoLens
        compares you to. These are open reference panels — not your nationality or ethnicity.
      </p>
      <h2>Regions</h2>
      <ul className="catalog-list">
        {regions.map((r) => (
          <li key={r.code}>
            <Link href={`/catalog/ancestry/${r.code}`}>{r.title}</Link>{" "}
            <span className="muted">({r.code})</span>
          </li>
        ))}
      </ul>
      <h2>Populations</h2>
      <ul className="catalog-list">
        {pops.map((p) => (
          <li key={p.code}>
            <Link href={`/catalog/ancestry/${p.code}`}>{p.title}</Link>{" "}
            <span className="muted">
              ({p.code}
              {p.region ? ` · ${p.region}` : ""})
            </span>
          </li>
        ))}
      </ul>
      <p>
        <Link href="/reports/ancestry">← Back to Ancestry Composition</Link>
      </p>
    </div>
  );
}
