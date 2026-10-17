type Point = {
  genetic_id?: string;
  group?: string;
  PC1: number;
  PC2: number;
};

type Props = {
  user?: { PC1: number; PC2: number } | null;
  points?: Point[];
  explainedVariance?: number[];
  isDemo?: boolean;
};

function groupColor(group: string, map: Map<string, string>) {
  if (!map.has(group)) {
    const palette = ["#0f6b5c", "#d4654a", "#c4a574", "#5c6b66", "#1b9e88", "#8b5a3c", "#0a4f44"];
    map.set(group, palette[map.size % palette.length]);
  }
  return map.get(group)!;
}

export function PcaScatter({ user, points = [], explainedVariance = [], isDemo }: Props) {
  if (!user || points.length === 0) {
    return (
      <p className="muted">
        PCA scatter unavailable{isDemo ? " (demo panel may be empty)" : ""}.
      </p>
    );
  }

  const xs = [...points.map((p) => p.PC1), user.PC1];
  const ys = [...points.map((p) => p.PC2), user.PC2];
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const pad = 0.08;
  const dx = maxX - minX || 1;
  const dy = maxY - minY || 1;
  const w = 420;
  const h = 280;
  const mx = 36;
  const my = 24;
  const plotW = w - mx * 2;
  const plotH = h - my * 2;

  const sx = (v: number) => mx + ((v - minX) / dx) * (1 - 2 * pad) * plotW + pad * plotW;
  const sy = (v: number) => my + plotH - (((v - minY) / dy) * (1 - 2 * pad) * plotH + pad * plotH);

  const colors = new Map<string, string>();
  const groups = [...new Set(points.map((p) => p.group || "other"))].slice(0, 8);

  const varCaption =
    explainedVariance.length >= 2
      ? `PC1 ${((explainedVariance[0] || 0) * 100).toFixed(1)}% · PC2 ${((explainedVariance[1] || 0) * 100).toFixed(1)}% variance`
      : null;

  return (
    <div className="pca-wrap">
      <svg viewBox={`0 0 ${w} ${h}`} className="pca-svg" role="img" aria-label="Ancient PCA scatter">
        <rect x={mx} y={my} width={plotW} height={plotH} fill="#f7f4ef" stroke="#e2ddd4" />
        {points.map((p, i) => (
          <circle
            key={`${p.genetic_id || i}-${i}`}
            cx={sx(p.PC1)}
            cy={sy(p.PC2)}
            r={3.5}
            fill={groupColor(p.group || "other", colors)}
            opacity={0.75}
          >
            <title>{`${p.group || "?"} (${p.genetic_id || ""})`}</title>
          </circle>
        ))}
        <path
          d={`M ${sx(user.PC1)} ${sy(user.PC2) - 8} L ${sx(user.PC1) + 7} ${sy(user.PC2) + 5} L ${sx(user.PC1) - 7} ${sy(user.PC2) + 5} Z`}
          fill="#d4654a"
          stroke="#0a4f44"
          strokeWidth={1}
        />
        <text x={sx(user.PC1) + 10} y={sy(user.PC2) + 4} fontSize="12" fill="#0a4f44" fontFamily="var(--font-body)">
          You
        </text>
        <text x={w / 2} y={h - 4} textAnchor="middle" fontSize="11" fill="#5c6b66">
          PC1
        </text>
        <text
          x={12}
          y={h / 2}
          textAnchor="middle"
          fontSize="11"
          fill="#5c6b66"
          transform={`rotate(-90 12 ${h / 2})`}
        >
          PC2
        </text>
      </svg>
      {varCaption && <p className="muted pca-caption">{varCaption}{isDemo ? " · demo panel" : ""}</p>}
      <ul className="pca-legend">
        {groups.map((g) => (
          <li key={g}>
            <span className="pie-swatch" style={{ background: groupColor(g, colors) }} />
            {g}
          </li>
        ))}
        <li>
          <span className="pie-swatch" style={{ background: "#d4654a", clipPath: "polygon(50% 0,100% 100%,0 100%)" }} />
          You
        </li>
      </ul>
    </div>
  );
}
