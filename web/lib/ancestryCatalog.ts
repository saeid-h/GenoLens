export type CatalogEntry = {
  code: string;
  title: string;
  kind: "region" | "population";
  region?: string;
  blurb: string;
};

/** First-party encyclopedic blurbs — reference populations, not nationalities. */
export const ANCESTRY_CATALOG: CatalogEntry[] = [
  {
    code: "AFR",
    title: "African",
    kind: "region",
    blurb:
      "Continental roll-up of 1000 Genomes African analysis populations (Yoruba, Luhya, African Caribbean, and related). Affinity here means your genotypes look closer to these reference panels than to others — not a country label.",
  },
  {
    code: "EUR",
    title: "European",
    kind: "region",
    blurb:
      "Roll-up of 1000 Genomes European panels (Finnish, British, Iberian, Tuscan, CEU). Southern European references (TSI, IBS) often attract West Asian genomes because 1000 Genomes lacks dedicated Iranian/Levant panels.",
  },
  {
    code: "EAS",
    title: "East Asian",
    kind: "region",
    blurb:
      "Roll-up of Han Chinese, Japanese, Kinh Vietnamese, and related East Asian 1000 Genomes populations. Useful for continental affinity, not ethnicity certificates.",
  },
  {
    code: "SAS",
    title: "South Asian",
    kind: "region",
    blurb:
      "Roll-up of Gujarati, Punjabi, Bengali, Telugu, and related South Asian panels. West Asian samples frequently show elevated SAS affinity because those panels are the nearest open proxies for broad West/South Eurasian diversity.",
  },
  {
    code: "AMR",
    title: "American",
    kind: "region",
    blurb:
      "Admixed American 1000 Genomes populations (Mexican, Colombian, Peruvian, Puerto Rican). Reflects recent colonial-era admixture patterns in those reference cohorts.",
  },
  {
    code: "GIH",
    title: "Gujarati Indian (Houston)",
    kind: "population",
    region: "SAS",
    blurb:
      "Gujarati Indian community sampled in Houston — a South Asian 1000 Genomes analysis population. High GIH affinity does not mean you are Gujarati; it means your chip genotypes resemble this open reference panel.",
  },
  {
    code: "PJL",
    title: "Punjabi (Lahore)",
    kind: "population",
    region: "SAS",
    blurb:
      "Punjabi reference from Lahore. Another South Asian panel often near West/South Eurasian genomes when MENA-specific references are missing.",
  },
  {
    code: "ITU",
    title: "Indian Telugu (UK)",
    kind: "population",
    region: "SAS",
    blurb:
      "Telugu-speaking Indian community in the UK. Part of the South Asian cluster used for fine-scale affinity under GenoLens.",
  },
  {
    code: "BEB",
    title: "Bengali (Bangladesh)",
    kind: "population",
    region: "SAS",
    blurb: "Bengali reference from Bangladesh — South Asian 1000 Genomes panel.",
  },
  {
    code: "STU",
    title: "Sri Lankan Tamil (UK)",
    kind: "population",
    region: "SAS",
    blurb: "Sri Lankan Tamil community in the UK — South Asian analysis population.",
  },
  {
    code: "TSI",
    title: "Toscani (Italy)",
    kind: "population",
    region: "EUR",
    blurb:
      "Tuscan Italian reference. Often a top European hit for West Asian samples because Southern European panels sit closer in genotype space than Northern European ones when Near Eastern references are absent.",
  },
  {
    code: "IBS",
    title: "Iberian (Spain)",
    kind: "population",
    region: "EUR",
    blurb:
      "Iberian Spanish reference. Similar role to TSI for Southern European affinity calls.",
  },
  {
    code: "CEU",
    title: "Utah residents (CEPH, Northern European)",
    kind: "population",
    region: "EUR",
    blurb:
      "Classic Northern/Western European CEPH Utah panel. Useful contrast when Southern European panels score higher.",
  },
  {
    code: "GBR",
    title: "British (England and Scotland)",
    kind: "population",
    region: "EUR",
    blurb: "British 1000 Genomes panel — Northwest European reference.",
  },
  {
    code: "FIN",
    title: "Finnish",
    kind: "population",
    region: "EUR",
    blurb: "Finnish reference with distinctive Northern European genetic drift.",
  },
  {
    code: "YRI",
    title: "Yoruba (Ibadan, Nigeria)",
    kind: "population",
    region: "AFR",
    blurb: "Yoruba Nigerian panel — widely used West African reference.",
  },
  {
    code: "LWK",
    title: "Luhya (Webuye, Kenya)",
    kind: "population",
    region: "AFR",
    blurb: "Luhya Kenyan panel — East African 1000 Genomes reference.",
  },
  {
    code: "ASW",
    title: "African Ancestry in SW USA",
    kind: "population",
    region: "AFR",
    blurb: "African ancestry in Southwest USA — admixed African American reference cohort.",
  },
  {
    code: "ACB",
    title: "African Caribbean (Barbados)",
    kind: "population",
    region: "AFR",
    blurb: "African Caribbean Barbados panel.",
  },
  {
    code: "CHB",
    title: "Han Chinese (Beijing)",
    kind: "population",
    region: "EAS",
    blurb: "Han Chinese Beijing panel — East Asian reference.",
  },
  {
    code: "JPT",
    title: "Japanese (Tokyo)",
    kind: "population",
    region: "EAS",
    blurb: "Japanese Tokyo panel — East Asian reference.",
  },
  {
    code: "CHS",
    title: "Southern Han Chinese",
    kind: "population",
    region: "EAS",
    blurb: "Southern Han Chinese 1000 Genomes panel.",
  },
  {
    code: "KHV",
    title: "Kinh (Ho Chi Minh City, Vietnam)",
    kind: "population",
    region: "EAS",
    blurb: "Kinh Vietnamese panel — Southeast/East Asian reference.",
  },
  {
    code: "CDX",
    title: "Chinese Dai (Xishuangbanna)",
    kind: "population",
    region: "EAS",
    blurb: "Chinese Dai panel from Xishuangbanna.",
  },
  {
    code: "MXL",
    title: "Mexican Ancestry (Los Angeles)",
    kind: "population",
    region: "AMR",
    blurb: "Mexican ancestry in Los Angeles — admixed American reference.",
  },
  {
    code: "PEL",
    title: "Peruvian (Lima)",
    kind: "population",
    region: "AMR",
    blurb: "Peruvian Lima panel with substantial Indigenous American ancestry in the cohort.",
  },
  {
    code: "CLM",
    title: "Colombian (Medellín)",
    kind: "population",
    region: "AMR",
    blurb: "Colombian Medellín admixed American panel.",
  },
  {
    code: "PUR",
    title: "Puerto Rican",
    kind: "population",
    region: "AMR",
    blurb: "Puerto Rican 1000 Genomes panel.",
  },
];

export function getCatalogEntry(code: string): CatalogEntry | undefined {
  return ANCESTRY_CATALOG.find((e) => e.code.toUpperCase() === code.toUpperCase());
}

export function catalogRegions() {
  return ANCESTRY_CATALOG.filter((e) => e.kind === "region");
}

export function catalogPopulations(region?: string) {
  return ANCESTRY_CATALOG.filter(
    (e) => e.kind === "population" && (!region || e.region === region)
  );
}
