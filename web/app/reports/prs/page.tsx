"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { HubIllustration } from "@/components/illustrations";
import { getPrs } from "@/lib/api";
import { useSample } from "@/lib/sample";

type VariantRow = {
  rsid: string;
  effect_allele: string;
  weight: number;
  genotype: string | null;
  dosage: number | null;
  contribution: number;
  present: boolean;
};

type ScoreRow = {
  id: string;
  trait: string;
  trait_plain?: string;
  what_it_is?: string;
  what_it_is_not?: string;
  citation?: string;
  raw_score: number;
  max_score_if_all_effect_alleles?: number;
  fraction_of_panel_max?: number | null;
  panel_band?: string;
  variants_used: number;
  variants_missing: number;
  variants_total?: number;
  coverage_percent?: number;
  coverage_note?: string;
  readout?: string;
  is_demo?: boolean;
  variants?: VariantRow[];
};

export default function PrsPage() {
  const { primaryId } = useSample();
  const [data, setData] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    if (!primaryId) return;
    getPrs(primaryId).then(setData).catch(() => setData(null));
  }, [primaryId]);

  const scores = (data?.scores || []) as ScoreRow[];
  const isDemo = Boolean(data?.is_demo);

  return (
    <div className="panel">
      <div className="prs-hero">
        <div className="prs-hero-art" aria-hidden>
          <HubIllustration name="prs" />
        </div>
        <div>
          <h1 style={{ marginTop: 0 }}>Polygenic scores</h1>
          <p>
            A <strong>polygenic score</strong> adds many small DNA effects for{" "}
            <em>one</em> trait into a single number: each scoring SNP contributes{" "}
            <code>(how many effect alleles you carry) × (study weight)</code>.
          </p>
          <p className="muted" style={{ marginBottom: 0 }}>
            It is an <strong>allele sum</strong>, not a measurement of your body and not a
            diagnosis. Coverage (how many of the score’s SNPs are on your chip) matters as much as
            the number itself.
          </p>
        </div>
      </div>

      {isDemo && (
        <div className="prs-mode-banner">
          <strong>Demo mode.</strong> You are seeing GenoLens’s tiny synthetic weight list so this
          page is readable. It is <em>not</em> a published PGS Catalog score and must not be read as
          height, BMI, or caffeine advice.
        </div>
      )}

      <details className="about-collapse">
        <summary>About this result / limits</summary>
        <Disclaimer text={data?.disclaimer} />
        <p>{data?.how_to_read}</p>
        <p className="muted">
          Source: {String(data?.source || "—")}. {String(data?.pgs_catalog_hint || "")}
        </p>
      </details>

      <div className="prs-card-grid">
        {scores.map((s) => {
          const frac = s.fraction_of_panel_max;
          const pct = frac == null ? null : Math.max(0, Math.min(100, frac * 100));
          return (
            <article key={s.id} className="prs-card">
              <div className="prs-card-top">
                <div>
                  <div className="prediction-topic">
                    {s.is_demo ? "Demo score" : "Catalog score"} · {s.id}
                  </div>
                  <h2 className="prs-card-title">{s.trait_plain || s.trait}</h2>
                </div>
              </div>
              <p className="prs-readout">{s.readout || `Raw score ${Number(s.raw_score).toFixed(4)}`}</p>
              <div className="prs-metrics">
                <div>
                  <div className="label">Raw allele sum</div>
                  <div className="value">{Number(s.raw_score).toFixed(4)}</div>
                </div>
                <div>
                  <div className="label">Panel max (all effect alleles)</div>
                  <div className="value">
                    {Number(s.max_score_if_all_effect_alleles || 0).toFixed(4)}
                  </div>
                </div>
                <div>
                  <div className="label">SNPs called</div>
                  <div className="value">
                    {s.variants_used}/{s.variants_total ?? s.variants_used + s.variants_missing}
                  </div>
                </div>
              </div>
              {pct != null && (
                <div className="prs-bar-block">
                  <div className="muted" style={{ marginBottom: "0.35rem" }}>
                    Where you sit on <em>this tiny panel only</em>
                    {s.panel_band ? ` — ${s.panel_band}` : ""}
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )}
              <p className="muted">{s.coverage_note}</p>
              <details className="prediction-how">
                <summary>What this is / is not</summary>
                <p>
                  <strong>Is:</strong> {s.what_it_is}
                </p>
                <p>
                  <strong>Is not:</strong> {s.what_it_is_not}
                </p>
                {s.citation && <p className="muted">{s.citation}</p>}
              </details>
              {s.variants && s.variants.length > 0 && (
                <details className="prediction-how">
                  <summary>SNP contributions</summary>
                  <table className="data">
                    <thead>
                      <tr>
                        <th>rsID</th>
                        <th>Your DNA</th>
                        <th>Effect allele</th>
                        <th>Dosage</th>
                        <th>Weight</th>
                        <th>Contribution</th>
                      </tr>
                    </thead>
                    <tbody>
                      {s.variants.map((v) => (
                        <tr key={v.rsid} style={{ opacity: v.present ? 1 : 0.55 }}>
                          <td>{v.rsid}</td>
                          <td>{v.genotype || "Not called"}</td>
                          <td>{v.effect_allele}</td>
                          <td>{v.dosage == null ? "—" : v.dosage}</td>
                          <td>{Number(v.weight).toFixed(3)}</td>
                          <td>{Number(v.contribution).toFixed(4)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </details>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
