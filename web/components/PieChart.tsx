type Slice = { code: string; label: string; percent: number };

const COLORS = ["#0f6b5c", "#1b9e88", "#d4654a", "#c4a574", "#5c6b66", "#0a4f44", "#e8a090"];

function polar(cx: number, cy: number, r: number, angleDeg: number) {
  const a = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

function arcPath(cx: number, cy: number, r: number, start: number, end: number) {
  const s = polar(cx, cy, r, end);
  const e = polar(cx, cy, r, start);
  const large = end - start > 180 ? 1 : 0;
  return `M ${cx} ${cy} L ${e.x} ${e.y} A ${r} ${r} 0 ${large} 1 ${s.x} ${s.y} Z`;
}

export function PieChart({ items }: { items: Slice[] }) {
  const sorted = [...items].filter((i) => i.percent > 0).sort((a, b) => b.percent - a.percent);
  const total = sorted.reduce((s, i) => s + i.percent, 0) || 1;
  const cx = 80;
  const cy = 80;
  const r = 70;
  let angle = 0;
  const slices = sorted.map((item, idx) => {
    const sweep = (item.percent / total) * 360;
    const start = angle;
    const end = angle + sweep;
    angle = end;
    return { item, start, end, color: COLORS[idx % COLORS.length] };
  });

  return (
    <div className="pie-wrap">
      <svg viewBox="0 0 160 160" className="pie-svg" role="img" aria-label="Regional affinity pie">
        {slices.length === 0 ? (
          <circle cx={cx} cy={cy} r={r} fill="#ebe6de" />
        ) : slices.length === 1 ? (
          <circle cx={cx} cy={cy} r={r} fill={slices[0].color} />
        ) : (
          slices.map(({ item, start, end, color }) => (
            <path key={item.code} d={arcPath(cx, cy, r, start, end)} fill={color} />
          ))
        )}
        <circle cx={cx} cy={cy} r={28} fill="#f7f4ef" />
      </svg>
      <ul className="pie-legend">
        {slices.map(({ item, color }) => (
          <li key={item.code}>
            <span className="pie-swatch" style={{ background: color }} />
            <span>
              {item.label}{" "}
              <span className="muted">{item.percent.toFixed(1)}%</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
