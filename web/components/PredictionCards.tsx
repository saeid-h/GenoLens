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
  research: "Research marker",
  pigmentation: "Pigmentation",
};

const TOPIC_RANK = [
  "eye_color",
  "bitter_taste",
  "earwax",
  "lactose",
  "skin_pigmentation",
  "hair_pigmentation",
  "caffeine",
  "muscle",
  "alcohol",
  "folate",
  "stress",
  "sleep",
  "drug_metabolism",
  "carrier",
  "clotting",
  "body_mass",
  "research",
];

function topicLabel(topic: string | null | undefined) {
  if (!topic) return "Marker";
  return TOPIC_LABELS[topic] || topic.replace(/_/g, " ");
}

/** One illustrated card per marker — title = what it is about; gene is labeled clearly. */
export function PredictionCards({ hits }: { hits: PredictionHit[] }) {
  const ordered = [...hits].sort((a, b) => {
    const ra = TOPIC_RANK.indexOf(a.topic || "research");
    const rb = TOPIC_RANK.indexOf(b.topic || "research");
    const da = ra === -1 ? 99 : ra;
    const db = rb === -1 ? 99 : rb;
    if (da !== db) return da - db;
    return (a.gene || a.rsid).localeCompare(b.gene || b.rsid);
  });

  return (
    <div className="prediction-grid">
      {ordered.map((h) => {
        const about = topicLabel(h.topic);
        const gene = h.gene || "Unknown gene";
        const headline =
          (h.present && (h.prediction || h.note)) ||
          (!h.present ? "Not called on this file" : "No prediction for this genotype");
        return (
          <article key={h.rsid} className={`prediction-card${h.present === false ? " dimmed" : ""}`}>
            <div className="prediction-art">
              <TopicIllustration topic={h.topic || "research"} />
            </div>
            <div className="prediction-body">
              <div className="prediction-topic">{about}</div>
              <h3 className="prediction-gene">{gene}</h3>
              <p className="prediction-headline">{headline}</p>
              <p className="muted prediction-meta">
                Your DNA: <strong>{h.genotype || "Not called"}</strong>
                <span aria-hidden> · </span>
                {h.rsid}
              </p>
              <details className="prediction-how">
                <summary>How to read this</summary>
                <p>{h.summary || "Exploratory genotype note — not medical advice."}</p>
                {h.note && h.note !== headline && <p>{h.note}</p>}
              </details>
            </div>
          </article>
        );
      })}
    </div>
  );
}
