"use client";

import type { PredictionHit } from "@/components/PredictionCards";

type Traits = {
  eye: string;
  hair: string;
  skin: string;
  legend: string[];
};

function infer(hits: PredictionHit[]): Traits {
  const byRsid = Object.fromEntries(hits.map((h) => [h.rsid, h]));
  const legend: string[] = [];

  let eye = "#5c4030";
  const herc = byRsid["rs12913832"];
  if (herc?.present && herc.genotype) {
    const g = herc.genotype;
    if (g === "GG") eye = "#5b8db8";
    else if (g === "AG" || g === "GA") eye = "#6b7a4a";
    else eye = "#3d2914";
    legend.push(`Eyes: ${herc.prediction || herc.note || herc.genotype} (${herc.rsid})`);
  }

  let hair = "#2c1810";
  const mc1r = byRsid["rs1805007"];
  if (mc1r?.present && mc1r.genotype) {
    if (mc1r.genotype === "TT" || mc1r.genotype === "CT" || mc1r.genotype === "TC") {
      hair = "#c44";
    }
    legend.push(`Hair tendency: ${mc1r.prediction || mc1r.note || mc1r.genotype} (${mc1r.rsid})`);
  }

  let skin = "#e0b896";
  const slc = byRsid["rs1426654"];
  if (slc?.present && slc.genotype) {
    const g = slc.genotype;
    if (g === "AA") skin = "#f0d5c4";
    else if (g === "GG") skin = "#8d5524";
    else skin = "#d2a679";
    legend.push(`Skin: ${slc.prediction || slc.note || slc.genotype} (${slc.rsid})`);
  }

  if (legend.length === 0) {
    legend.push("Not enough pigmentation markers called — showing a neutral sketch.");
  }

  return { eye, hair, skin, legend };
}

export function PhenotypeSketch({ hits }: { hits: PredictionHit[] }) {
  const t = infer(hits);
  return (
    <div className="phenotype-wrap">
      <div className="phenotype-art-box">
        <svg viewBox="0 0 160 180" className="phenotype-svg" role="img" aria-label="Playful phenotype sketch">
          <rect width="160" height="180" fill="#eef7f4" rx="12" />
          <ellipse cx="80" cy="100" rx="42" ry="52" fill={t.skin} />
          <path
            d="M40 78 Q80 20 120 78 Q100 48 80 52 Q60 48 40 78"
            fill={t.hair}
          />
          <ellipse cx="62" cy="95" rx="8" ry="10" fill="#fff" />
          <ellipse cx="98" cy="95" rx="8" ry="10" fill="#fff" />
          <circle cx="62" cy="96" r="5" fill={t.eye} />
          <circle cx="98" cy="96" r="5" fill={t.eye} />
          <circle cx="60" cy="94" r="1.5" fill="#fff" />
          <circle cx="96" cy="94" r="1.5" fill="#fff" />
          <path d="M72 118 Q80 126 88 118" fill="none" stroke="#8b5a3c" strokeWidth="2.5" strokeLinecap="round" />
          <ellipse cx="80" cy="108" rx="4" ry="3" fill="#c9977a" opacity="0.5" />
        </svg>
      </div>
      <div>
        <h3 style={{ fontFamily: "var(--font-display)", marginTop: 0 }}>Phenotype sketch</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Playful illustration from a few SNPs — not a photo or identity portrait.
        </p>
        <ul className="phenotype-legend">
          {t.legend.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
