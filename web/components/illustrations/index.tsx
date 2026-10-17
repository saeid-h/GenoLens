/** Illustrated SVG tiles for report hubs and trait topics — pictorial, not tiny glyphs. */

type IllProps = { className?: string; title?: string };

const base = {
  width: "100%",
  height: "100%",
  viewBox: "0 0 160 100",
  preserveAspectRatio: "xMidYMid slice" as const,
  "aria-hidden": true as const,
};

export function IllAncestry({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <defs>
        <linearGradient id="anc-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#d8efe8" />
          <stop offset="100%" stopColor="#f7f4ef" />
        </linearGradient>
      </defs>
      <rect width="160" height="100" fill="url(#anc-sky)" />
      <ellipse cx="80" cy="58" rx="48" ry="28" fill="#0f6b5c" opacity="0.18" />
      <ellipse cx="80" cy="58" rx="48" ry="28" fill="none" stroke="#0f6b5c" strokeWidth="2" />
      <path
        d="M32 58 Q55 30 80 58 Q105 86 128 58"
        fill="none"
        stroke="#d4654a"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx="55" cy="42" r="4" fill="#d4654a" />
      <circle cx="105" cy="72" r="4" fill="#0f6b5c" />
      <circle cx="80" cy="58" r="5" fill="#0a4f44" />
    </svg>
  );
}

export function IllHaplogroups({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#eef7f4" />
      <path d="M80 18 V78" stroke="#0f6b5c" strokeWidth="2.5" />
      <path d="M80 40 H45 M80 40 H115 M45 40 V62 M115 40 V62" stroke="#0f6b5c" strokeWidth="2" />
      <circle cx="80" cy="18" r="7" fill="#d4654a" />
      <circle cx="45" cy="62" r="6" fill="#0f6b5c" />
      <circle cx="115" cy="62" r="6" fill="#0f6b5c" />
      <circle cx="80" cy="78" r="6" fill="#0a4f44" />
    </svg>
  );
}

export function IllTraits({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#fff5f0" />
      <ellipse cx="80" cy="52" rx="28" ry="34" fill="#f0d5c4" />
      <ellipse cx="68" cy="48" rx="5" ry="6" fill="#3d2914" />
      <ellipse cx="92" cy="48" rx="5" ry="6" fill="#3d2914" />
      <path d="M70 66 Q80 72 90 66" fill="none" stroke="#8b5a3c" strokeWidth="2" />
      <path d="M52 38 Q80 18 108 38" fill="none" stroke="#2c1810" strokeWidth="6" strokeLinecap="round" />
    </svg>
  );
}

export function IllWellness({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#eef7f4" />
      <circle cx="80" cy="50" r="28" fill="none" stroke="#0f6b5c" strokeWidth="3" />
      <path d="M80 28 V50 L98 62" stroke="#d4654a" strokeWidth="3" strokeLinecap="round" />
      <circle cx="80" cy="50" r="4" fill="#0a4f44" />
    </svg>
  );
}

export function IllPharma({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#f5f0ea" />
      <rect x="48" y="28" width="64" height="28" rx="14" fill="#d4654a" />
      <rect x="48" y="52" width="64" height="28" rx="14" fill="#0f6b5c" />
      <line x1="48" y1="52" x2="112" y2="52" stroke="#f7f4ef" strokeWidth="2" />
    </svg>
  );
}

export function IllHealth({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#eef7f4" />
      <path
        d="M80 78 C40 52 48 28 80 40 C112 28 120 52 80 78Z"
        fill="#d4654a"
        opacity="0.85"
      />
      <rect x="74" y="44" width="12" height="28" rx="2" fill="#fff" />
      <rect x="66" y="52" width="28" height="12" rx="2" fill="#fff" />
    </svg>
  );
}

export function IllRelatives({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#eef7f4" />
      <line x1="80" y1="32" x2="80" y2="48" stroke="#5c6b66" strokeWidth="2" />
      <line x1="48" y1="48" x2="112" y2="48" stroke="#5c6b66" strokeWidth="2" />
      <line x1="48" y1="48" x2="48" y2="58" stroke="#5c6b66" strokeWidth="2" />
      <line x1="112" y1="48" x2="112" y2="58" stroke="#5c6b66" strokeWidth="2" />
      <line x1="80" y1="48" x2="80" y2="72" stroke="#5c6b66" strokeWidth="2" />
      <circle cx="80" cy="22" r="10" fill="#0a4f44" />
      <circle cx="48" cy="68" r="10" fill="#0f6b5c" />
      <circle cx="112" cy="68" r="10" fill="#0f6b5c" />
      <circle cx="80" cy="82" r="9" fill="#d4654a" />
    </svg>
  );
}

export function IllAncient({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <defs>
        <linearGradient id="anc-dune" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e8dcc8" />
          <stop offset="100%" stopColor="#c4a574" />
        </linearGradient>
      </defs>
      <rect width="160" height="100" fill="url(#anc-dune)" />
      <path d="M20 78 L45 40 L70 78 Z" fill="#8b7355" />
      <path d="M70 78 L95 48 L120 78 Z" fill="#6b5640" />
      <circle cx="130" cy="28" r="10" fill="#d4654a" opacity="0.7" />
      <circle cx="55" cy="70" r="3" fill="#0a4f44" />
    </svg>
  );
}

export function IllArchaic({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#ebe6de" />
      <ellipse cx="70" cy="55" rx="32" ry="28" fill="#a89078" />
      <ellipse cx="58" cy="50" rx="4" ry="5" fill="#3d2914" />
      <ellipse cx="82" cy="50" rx="4" ry="5" fill="#3d2914" />
      <path d="M58 68 Q70 74 82 68" fill="none" stroke="#5c4030" strokeWidth="2" />
      <path d="M42 42 Q70 22 98 42" fill="#6b5340" />
      <text x="118" y="38" fontSize="22" fill="#0f6b5c" fontFamily="Georgia, serif">
        N
      </text>
    </svg>
  );
}

export function IllPrs({ className }: IllProps) {
  return (
    <svg {...base} className={className}>
      <rect width="160" height="100" fill="#eef7f4" />
      <polyline
        points="20,75 40,55 55,62 75,35 95,48 115,28 140,40"
        fill="none"
        stroke="#0f6b5c"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="115" cy="28" r="5" fill="#d4654a" />
    </svg>
  );
}

/* Topic illustrations */
export function IllEye({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#eef7f4" />
      <ellipse cx="60" cy="40" rx="38" ry="22" fill="#fff" stroke="#0f6b5c" strokeWidth="2" />
      <circle cx="60" cy="40" r="14" fill="#3d5a40" />
      <circle cx="60" cy="40" r="6" fill="#1c2421" />
      <circle cx="55" cy="35" r="3" fill="#fff" opacity="0.8" />
    </svg>
  );
}

export function IllTaste({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#fff5f0" />
      <ellipse cx="60" cy="42" rx="28" ry="22" fill="#e8a090" />
      <path d="M40 42 Q60 58 80 42" fill="#d4654a" />
      <circle cx="48" cy="28" r="3" fill="#0f6b5c" />
      <circle cx="72" cy="26" r="3" fill="#0f6b5c" />
    </svg>
  );
}

export function IllEarwax({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#f5f0ea" />
      <path
        d="M45 20 C70 15 85 30 78 50 C72 68 50 72 42 58 C38 50 42 42 52 40 C60 38 62 48 55 52"
        fill="none"
        stroke="#0f6b5c"
        strokeWidth="4"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IllCaffeine({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#ebe6de" />
      <rect x="35" y="28" width="40" height="36" rx="4" fill="#0f6b5c" />
      <path d="M75 35 H88 Q95 35 95 45 Q95 55 88 55 H75" fill="none" stroke="#0f6b5c" strokeWidth="3" />
      <path d="M45 22 Q50 12 55 22 Q60 12 65 22" fill="none" stroke="#d4654a" strokeWidth="2" />
    </svg>
  );
}

export function IllLactose({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#eef7f4" />
      <ellipse cx="60" cy="48" rx="22" ry="26" fill="#fff" stroke="#cfe6df" strokeWidth="2" />
      <rect x="52" y="18" width="16" height="12" rx="2" fill="#0f6b5c" />
      <ellipse cx="60" cy="42" rx="10" ry="6" fill="#f0ebe3" />
    </svg>
  );
}

export function IllMuscle({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#eef7f4" />
      <path d="M30 55 Q45 25 60 40 Q75 25 90 55" fill="#0f6b5c" opacity="0.7" />
      <circle cx="60" cy="28" r="8" fill="#d4654a" />
    </svg>
  );
}

export function IllSkin({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#f7f4ef" />
      <circle cx="35" cy="40" r="16" fill="#f5d0b0" />
      <circle cx="60" cy="40" r="16" fill="#d2a679" />
      <circle cx="85" cy="40" r="16" fill="#8d5524" />
    </svg>
  );
}

export function IllHair({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#fff5f0" />
      <circle cx="60" cy="48" r="22" fill="#f0d5c4" />
      <path d="M38 42 Q60 8 82 42 Q70 28 60 30 Q50 28 38 42" fill="#c44" />
    </svg>
  );
}

export function IllAlcohol({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#f5f0ea" />
      <path d="M50 20 H70 L65 35 H55 Z" fill="#0f6b5c" />
      <rect x="48" y="35" width="24" height="30" rx="2" fill="#d4654a" opacity="0.85" />
      <line x1="48" y1="45" x2="72" y2="45" stroke="#fff" strokeWidth="1.5" opacity="0.5" />
    </svg>
  );
}

export function IllFolate({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#eef7f4" />
      <ellipse cx="50" cy="40" rx="14" ry="20" fill="#0f6b5c" transform="rotate(-20 50 40)" />
      <ellipse cx="70" cy="40" rx="14" ry="20" fill="#1b9e88" transform="rotate(20 70 40)" />
      <rect x="58" y="55" width="4" height="12" fill="#0a4f44" />
    </svg>
  );
}

export function IllDrug({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#f5f0ea" />
      <circle cx="45" cy="40" r="16" fill="#d4654a" />
      <circle cx="75" cy="40" r="16" fill="#0f6b5c" />
      <rect x="45" y="28" width="30" height="24" fill="#f5f0ea" />
    </svg>
  );
}

export function IllCarrier({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#eef7f4" />
      <circle cx="60" cy="40" r="24" fill="none" stroke="#0f6b5c" strokeWidth="3" />
      <text
        x="60"
        y="48"
        textAnchor="middle"
        fontSize="22"
        fill="#d4654a"
        fontFamily="Georgia, serif"
        fontWeight="600"
      >
        ?
      </text>
    </svg>
  );
}

export function IllGeneric({ className }: IllProps) {
  return (
    <svg {...base} className={className} viewBox="0 0 120 80">
      <rect width="120" height="80" fill="#ebe6de" />
      <circle cx="60" cy="40" r="18" fill="#0f6b5c" opacity="0.35" />
      <circle cx="60" cy="40" r="8" fill="#0a4f44" />
    </svg>
  );
}

export function IllEmptyRelatives({ className }: IllProps) {
  return (
    <svg
      className={className}
      width="100%"
      height="100%"
      viewBox="0 0 280 140"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden
    >
      <rect width="280" height="140" fill="#eef7f4" rx="12" />
      <circle cx="140" cy="36" r="14" fill="#cfe6df" />
      <circle cx="90" cy="90" r="14" fill="#cfe6df" />
      <circle cx="190" cy="90" r="14" fill="#cfe6df" />
      <path
        d="M140 50 V70 M90 70 H190 M90 70 V76 M190 70 V76"
        stroke="#a8cfc4"
        strokeWidth="2"
        strokeDasharray="4 3"
      />
      <text x="140" y="128" textAnchor="middle" fill="#5c6b66" fontSize="12" fontFamily="system-ui">
        Select relatives, then Compare
      </text>
    </svg>
  );
}

export const HUB_ILLUSTRATIONS = {
  ancestry: IllAncestry,
  haplogroups: IllHaplogroups,
  traits: IllTraits,
  wellness: IllWellness,
  pharmacogenetics: IllPharma,
  health: IllHealth,
  relatives: IllRelatives,
  ancient: IllAncient,
  archaic: IllArchaic,
  prs: IllPrs,
} as const;

export type HubIllustrationKey = keyof typeof HUB_ILLUSTRATIONS;

export const TOPIC_ILLUSTRATIONS: Record<string, (p: IllProps) => JSX.Element> = {
  eye_color: IllEye,
  bitter_taste: IllTaste,
  earwax: IllEarwax,
  caffeine: IllCaffeine,
  lactose: IllLactose,
  muscle: IllMuscle,
  skin_pigmentation: IllSkin,
  hair_pigmentation: IllHair,
  alcohol: IllAlcohol,
  folate: IllFolate,
  drug_metabolism: IllDrug,
  carrier: IllCarrier,
  stress: IllWellness,
  sleep: IllWellness,
  body_mass: IllGeneric,
  research: IllGeneric,
  clotting: IllHealth,
  pigmentation: IllSkin,
};

export function HubIllustration({
  name,
  className,
}: {
  name: HubIllustrationKey | string;
  className?: string;
}) {
  const Comp = HUB_ILLUSTRATIONS[name as HubIllustrationKey] || IllGeneric;
  return <Comp className={className} />;
}

export function TopicIllustration({ topic, className }: { topic: string; className?: string }) {
  const Comp = TOPIC_ILLUSTRATIONS[topic] || IllGeneric;
  return <Comp className={className} />;
}
