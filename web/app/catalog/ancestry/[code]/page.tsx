import Link from "next/link";
import { notFound } from "next/navigation";
import { ANCESTRY_CATALOG, getCatalogEntry } from "@/lib/ancestryCatalog";

export function generateStaticParams() {
  return ANCESTRY_CATALOG.map((e) => ({ code: e.code }));
}

export default function AncestryCatalogEntryPage({ params }: { params: { code: string } }) {
  const entry = getCatalogEntry(params.code);
  if (!entry) notFound();

  return (
    <div className="panel">
      <p className="muted" style={{ marginTop: 0 }}>
        <Link href="/catalog/ancestry">Ancestry catalog</Link>
        {entry.region ? (
          <>
            {" · "}
            <Link href={`/catalog/ancestry/${entry.region}`}>{entry.region}</Link>
          </>
        ) : null}
      </p>
      <h1>
        {entry.title} <span className="muted">({entry.code})</span>
      </h1>
      <p className="muted">{entry.kind === "region" ? "Continental region" : "1000 Genomes population"}</p>
      <p style={{ fontSize: "1.05rem", maxWidth: "40rem" }}>{entry.blurb}</p>
      <p className="muted">
        GenoLens reports affinity to these open references. A high percentage is not proof of
        descent from a named modern nationality.
      </p>
      <p>
        <Link href="/reports/ancestry">← Ancestry Composition</Link>
      </p>
    </div>
  );
}
