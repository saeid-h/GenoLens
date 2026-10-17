type Node = { label: string; generation: number; role: string; sex?: string | null };
type Edge = {
  source: string;
  target: string;
  kind: string;
  shared_cm: number;
  directed: boolean;
  note?: string;
};

type LayoutNode = Node & { x: number; y: number };

function layoutNodes(nodes: Node[], width: number, rowH: number): LayoutNode[] {
  const gens = Array.from(new Set(nodes.map((n) => n.generation))).sort((a, b) => a - b);
  const laid: LayoutNode[] = [];
  gens.forEach((g, gi) => {
    const row = nodes.filter((n) => n.generation === g);
    row.forEach((n, i) => {
      const x = ((i + 1) / (row.length + 1)) * width;
      const y = 48 + gi * rowH;
      laid.push({ ...n, x, y });
    });
  });
  return laid;
}

export function PedigreeView({
  nodes,
  edges,
  notes,
}: {
  nodes: Node[];
  edges: Edge[];
  notes?: string[];
}) {
  const width = 720;
  const rowH = 110;
  const gens = Array.from(new Set(nodes.map((n) => n.generation))).sort((a, b) => a - b);
  const height = Math.max(160, 40 + gens.length * rowH);
  const laid = layoutNodes(nodes, width, rowH);
  const byLabel = Object.fromEntries(laid.map((n) => [n.label, n]));

  return (
    <div>
      <svg
        className="pedigree-svg"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Directed pedigree"
        style={{ width: "100%", maxWidth: width, height: "auto" }}
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#0f6b5c" />
          </marker>
        </defs>
        {edges.map((e, i) => {
          const a = byLabel[e.source];
          const b = byLabel[e.target];
          if (!a || !b) return null;
          const midY = (a.y + b.y) / 2;
          const isSib = e.kind === "sibling";
          const dash = e.directed || isSib ? undefined : "6 5";
          const color = isSib ? "#8a5a44" : "#0f6b5c";
          if (isSib) {
            return (
              <path
                key={`e-${i}`}
                d={`M ${a.x} ${a.y + 28} Q ${(a.x + b.x) / 2} ${a.y + 52} ${b.x} ${b.y + 28}`}
                fill="none"
                stroke={color}
                strokeWidth={2}
              />
            );
          }
          return (
            <path
              key={`e-${i}`}
              d={`M ${a.x} ${a.y + 32} C ${a.x} ${midY}, ${b.x} ${midY}, ${b.x} ${b.y - 28}`}
              fill="none"
              stroke={color}
              strokeWidth={2.2}
              strokeDasharray={dash}
              markerEnd={e.directed ? "url(#arrow)" : undefined}
            />
          );
        })}
        {laid.map((n) => (
          <g key={n.label} transform={`translate(${n.x}, ${n.y})`}>
            <rect
              x={-64}
              y={-28}
              width={128}
              height={56}
              rx={12}
              fill="#ffffff"
              stroke="#0f6b5c"
              strokeWidth={1.5}
            />
            <text textAnchor="middle" y={-6} fontSize={11} fill="#5c6b66">
              {n.role}
            </text>
            <text textAnchor="middle" y={14} fontSize={14} fontWeight={600} fill="#1c2421">
              {n.label}
            </text>
          </g>
        ))}
      </svg>
      <table className="data">
        <thead>
          <tr>
            <th>From</th>
            <th>To</th>
            <th>Kind</th>
            <th>cM</th>
            <th>Directed</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody>
          {edges.map((e, i) => (
            <tr key={`${e.source}-${e.target}-${i}`}>
              <td>{e.source}</td>
              <td>{e.target}</td>
              <td>{e.kind}</td>
              <td>{e.shared_cm.toFixed(0)}</td>
              <td>{e.directed ? "parent → child" : "undirected / review"}</td>
              <td>{e.note || ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {notes && notes.length > 0 && (
        <ul className="muted">
          {notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
