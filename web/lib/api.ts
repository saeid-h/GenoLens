const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export type Sample = {
  id: string;
  label: string;
  filename: string;
  meta?: Record<string, unknown>;
};

export function getSamples() {
  return api<{ samples: Sample[]; default_primary_id: string | null; disclaimer: string }>(
    "/api/samples"
  );
}

export function getOverview(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/overview`);
}

export function getAncestry(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/ancestry`);
}

export function getHaplogroups(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/haplogroups`);
}

export function getTraits(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/traits`);
}

export function getWellness(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/wellness`);
}

export function getPharma(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/pharmacogenetics`);
}

export function getHealth(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/health`);
}

export function compare(primaryId: string, candidateIds: string[]) {
  return api<Record<string, unknown>>("/api/compare", {
    method: "POST",
    body: JSON.stringify({ primary_id: primaryId, candidate_ids: candidateIds }),
  });
}

export function familyTree(primaryId: string, candidateIds: string[]) {
  return api<Record<string, unknown>>("/api/family-tree", {
    method: "POST",
    body: JSON.stringify({ primary_id: primaryId, candidate_ids: candidateIds }),
  });
}

export function getAncient(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/ancient`);
}

export function getArchaic(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/archaic`);
}

export function getPrs(id: string) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/prs`);
}

export function putMeta(id: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/api/samples/${encodeURIComponent(id)}/meta`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export const REPORTS = [
  {
    slug: "ancestry",
    title: "Ancestry Composition",
    blurb: "Continental affinity percentages",
    illustration: "ancestry",
  },
  {
    slug: "haplogroups",
    title: "Haplogroups",
    blurb: "Maternal and paternal lineage hints",
    illustration: "haplogroups",
  },
  {
    slug: "traits",
    title: "Traits",
    blurb: "Taste, pigmentation, and similar markers",
    illustration: "traits",
  },
  {
    slug: "wellness",
    title: "Wellness",
    blurb: "Metabolism-oriented exploratory markers",
    illustration: "wellness",
  },
  {
    slug: "pharmacogenetics",
    title: "Pharmacogenetics",
    blurb: "Drug-gene markers with caveats",
    illustration: "pharmacogenetics",
  },
  {
    slug: "health",
    title: "Health & carrier",
    blurb: "Exploratory cards — not diagnoses",
    illustration: "health",
  },
  {
    slug: "relatives",
    title: "DNA Relatives",
    blurb: "Primary vs selected candidates + tree",
    illustration: "relatives",
  },
  {
    slug: "ancient",
    title: "Ancient affinity",
    blurb: "Closest ancient groups and individuals",
    illustration: "ancient",
  },
  {
    slug: "archaic",
    title: "Archaic affinity",
    blurb: "Neanderthal-informative SNP hits",
    illustration: "archaic",
  },
  {
    slug: "prs",
    title: "Polygenic scores",
    blurb: "Open-catalog / demo PRS scores",
    illustration: "prs",
  },
] as const;
