type Props = {
  items: { code: string; label: string; percent: number }[];
};

export function PercentBars({ items }: Props) {
  const sorted = [...items].sort((a, b) => b.percent - a.percent);
  return (
    <div>
      {sorted.map((item) => (
        <div className="bar-row" key={item.code}>
          <div>{item.label}</div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${Math.min(100, item.percent)}%` }} />
          </div>
          <div style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
            {item.percent.toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
}
