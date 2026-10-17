"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { REPORTS } from "@/lib/api";
import { useSample } from "@/lib/sample";

export function ReportShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { samples, primaryId, setPrimaryId, loading, error } = useSample();
  const primary = samples.find((s) => s.id === primaryId);

  return (
    <div className="shell">
      <header className="topbar">
        <Link href="/" className="brand">
          Geno<span>Lens</span>
        </Link>
        <div className="topbar-meta">
          {loading ? (
            "Loading samples…"
          ) : error ? (
            <span>API offline — start uvicorn on :8000</span>
          ) : (
            <label>
              Primary{" "}
              <select value={primaryId} onChange={(e) => setPrimaryId(e.target.value)}>
                {samples.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
      </header>
      <div className="layout">
        <aside className="nav">
          <h2>Reports</h2>
          <Link href="/reports" className={pathname === "/reports" ? "active" : ""}>
            Hub
          </Link>
          {REPORTS.map((r) => {
            const href = `/reports/${r.slug}`;
            return (
              <Link key={r.slug} href={href} className={pathname === href ? "active" : ""}>
                {r.title}
              </Link>
            );
          })}
          <h2 style={{ marginTop: "1.5rem" }}>Settings</h2>
          <Link
            href="/settings/samples"
            className={pathname === "/settings/samples" ? "active" : ""}
          >
            Samples & ages
          </Link>
        </aside>
        <main className="main">
          {primary && pathname.startsWith("/reports") && (
            <p className="muted" style={{ marginTop: 0 }}>
              Viewing reports for <strong>{primary.label}</strong>
            </p>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
