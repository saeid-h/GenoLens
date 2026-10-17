"use client";

import { TopicIllustration } from "@/components/illustrations";

export type PredictionHit = {
  rsid: string;
  gene?: string;
  category?: string;
  genotype?: string | null;
  note?: string;
  summary?: string;
  present?: boolean;
  topic?: string | null;
  prediction?: string | null;
};

const TOPIC_LABELS: Record<string, string> = {
  eye_color: "Eye color",
  bitter_taste: "Bitter taste",
  earwax: "Earwax",
  caffeine: "Caffeine",
  lactose: "Lactose",
  muscle: "Muscle",
  skin_pigmentation: "Skin pigmentation",
  hair_pigmentation: "Hair / fair skin",
  alcohol: "Alcohol",
  folate: "Folate",
  drug_metabolism: "Drug metabolism",
  carrier: "Carrier-style",
  stress: "Stress chemistry",
  sleep: "Sleep timing",
  body_mass: "Body mass research",
  clotting: "Clotting markers",
  research: "Research markers",
  pigmentation: "Pigmentation",
};

function topicLabel(topic: string) {
  return TOPIC_LABELS[topic] || topic.replace(/_/g, " ");
}

export function PredictionCards({ hits }: { hits: PredictionHit[] }) {
  const groups = new Map<string, PredictionHit[]>();
  for (const h of hits) {
    const key = h.topic || "research";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(h);
  }

  // Prefer present hits with a prediction as the group headline
  const ordered = [...groups.entries()].sort((a, b) => {
    const rank = (k: string) =>
      ["eye_color", "bitter_taste", "earwax", "lactose", "skin_pigmentation", "hair_pigmentation", "caffeine", "muscle", "alcohol", "folate"].indexOf(
        k
      );
    const ra = rank(a[0]);
    const rb = rank(b[0]);
    return (ra === -1 ? 99 : ra) - (rb === -1 ? 99 : rb);
  });

  return (
    <div className="prediction-grid">
      {ordered.map(([topic, groupHits]) => {
        const headline =
          groupHits.find((h) => h.present && h.prediction)?.prediction ||
          groupHits.find((h) => h.present)?.note ||
          "Not called on this file";
        const primary = groupHits.find((h) => h.present && h.prediction) || groupHits[0];
        return (
          <article key={topic} className="prediction-card">
            <div className="prediction-art">
              <TopicIllustration topic={topic} />
            </div>
            <div className="prediction-body">
              <div className="prediction-topic">{topicLabel(topic)}</div>
              <h3 className="prediction-headline">{headline}</h3>
              <p className="muted prediction-meta">
                {primary?.gene || "—"} · {primary?.genotype || "Not called"} · {primary?.rsid}
              </p>
              {groupHits.length > 1 && (
                <ul className="prediction-extra">
                  {groupHits
                    .filter((h) => h !== primary)
                    .map((h) => (
                      <li key={h.rsid}>
                        <strong>{h.prediction || h.summary || h.rsid}</strong>
                        <span className="muted">
                          {" "}
                          · {h.genotype || "not called"} · {h.rsid}
                        </span>
                      </li>
                    ))}
                </ul>
              )}
              <details className="prediction-how">
                <summary>How to read this</summary>
                <p>{primary?.summary || "Exploratory genotype note — not medical advice."}</p>
                {primary?.note && primary.note !== headline && <p>{primary.note}</p>}
              </details>
            </div>
          </article>
        );
      })}
    </div>
  );
}
