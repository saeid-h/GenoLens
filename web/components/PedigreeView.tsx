type Node = {
  label: string;
  generation: number;
  role: string;
  sex?: string | null;
  birth_year?: number | null;
};
type Edge = {
  source: string;
  target: string;
  kind: string;
  shared_cm: number;
  directed: boolean;
  note?: string;
};

export function PedigreeView({
  nodes,
  edges,
  notes,
  birthYears,
  asciiTree,
}: {
  nodes: Node[];
  edges: Edge[];
  notes?: string[];
  birthYears?: Record<string, number | null>;
  asciiTree?: string;
}) {
  const gens = Array.from(new Set(nodes.map((n) => n.generation))).sort((a, b) => a - b);
  const pc = edges.filter((e) => e.kind === "parent_child");
  const sibs = edges.filter((e) => e.kind === "sibling");

  return (
    <div className="pedigree-wrap">
      <div className="pedigree" aria-label="Family tree by generation">
        {gens.map((g) => (
          <div key={g} className="generation-block">
            <div className="generation-label">Generation {g}</div>
            <div className="generation">
              {nodes
                .filter((n) => n.generation === g)
                .map((n) => {
                  const year = n.birth_year ?? birthYears?.[n.label];
                  return (
                    <div className="person" key={n.label}>
                      <div className="role">{n.role}</div>
                      <div className="name">{n.label}</div>
                      <div className="muted">
                        {[n.sex, year != null ? `b. ${year}` : null].filter(Boolean).join(" · ") || "—"}
                      </div>
                    </div>
                  );
                })}
            </div>
            {g < (gens[gens.length - 1] ?? g) && pc.some((e) => true) ? (
              <div className="pedigree-arrows" aria-hidden>
                ↓ parent → child
              </div>
            ) : null}
          </div>
        ))}
      </div>

      {pc.length > 0 && (
        <>
          <h3>Parent → child links</h3>
          <ul className="edge-list">
            {pc.map((e, i) => (
              <li key={`pc-${i}`}>
                <strong>
                  {e.source} {e.directed ? "→" : "—"} {e.target}
                </strong>{" "}
                <span className="muted">
                  ({e.shared_cm.toFixed(0)} cM
                  {e.directed ? "" : ", direction unclear"}
                  {e.note ? ` — ${e.note}` : ""})
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      {sibs.length > 0 && (
        <>
          <h3>Same-generation links</h3>
          <ul className="edge-list">
            {sibs.map((e, i) => (
              <li key={`sib-${i}`}>
                <strong>
                  {e.source} ↔ {e.target}
                </strong>{" "}
                <span className="muted">
                  ({e.shared_cm.toFixed(0)} cM sibling-range
                  {e.note ? ` — ${e.note}` : ""})
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

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

      {asciiTree ? (
        <pre className="ascii-tree" aria-label="ASCII pedigree">
          {asciiTree}
        </pre>
      ) : null}

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
