"use client";

import { useLayoutEffect, useRef, useState } from "react";

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

type Line = { x1: number; y1: number; x2: number; y2: number; kind: string };

export function PedigreeView({
  nodes,
  edges,
  notes,
  birthYears,
  asciiTree,
  detailsCollapsed = false,
}: {
  nodes: Node[];
  edges: Edge[];
  notes?: string[];
  birthYears?: Record<string, number | null>;
  asciiTree?: string;
  detailsCollapsed?: boolean;
}) {
  const gens = Array.from(new Set(nodes.map((n) => n.generation))).sort((a, b) => a - b);
  const pc = edges.filter((e) => e.kind === "parent_child");
  const sibs = edges.filter((e) => e.kind === "sibling");

  const wrapRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const [lines, setLines] = useState<Line[]>([]);
  const [size, setSize] = useState({ w: 0, h: 0 });

  const setNodeRef = (label: string, el: HTMLDivElement | null) => {
    if (el) nodeRefs.current.set(label, el);
    else nodeRefs.current.delete(label);
  };

  useLayoutEffect(() => {
    const wrap = wrapRef.current;
    if (!wrap) return;

    const measure = () => {
      const wr = wrap.getBoundingClientRect();
      const next: Line[] = [];
      const mid = (el: HTMLElement) => {
        const r = el.getBoundingClientRect();
        return {
          cx: r.left - wr.left + r.width / 2,
          top: r.top - wr.top,
          bottom: r.bottom - wr.top,
        };
      };

      for (const e of edges.filter((x) => x.kind === "parent_child")) {
        const a = nodeRefs.current.get(e.source);
        const b = nodeRefs.current.get(e.target);
        if (!a || !b) continue;
        const pa = mid(a);
        const pb = mid(b);
        const parentIsAbove = pa.bottom <= pb.top;
        if (parentIsAbove) {
          next.push({ x1: pa.cx, y1: pa.bottom, x2: pb.cx, y2: pb.top, kind: "parent_child" });
        } else {
          next.push({ x1: pb.cx, y1: pb.bottom, x2: pa.cx, y2: pa.top, kind: "parent_child" });
        }
      }

      for (const e of edges.filter((x) => x.kind === "sibling")) {
        const a = nodeRefs.current.get(e.source);
        const b = nodeRefs.current.get(e.target);
        if (!a || !b) continue;
        const pa = mid(a);
        const pb = mid(b);
        const y = Math.min(pa.top, pb.top) - 10;
        next.push({ x1: pa.cx, y1: pa.top, x2: pa.cx, y2: y, kind: "sibling" });
        next.push({ x1: pb.cx, y1: pb.top, x2: pb.cx, y2: y, kind: "sibling" });
        next.push({ x1: pa.cx, y1: y, x2: pb.cx, y2: y, kind: "sibling" });
      }

      setLines(next);
      setSize({ w: wrap.scrollWidth, h: wrap.scrollHeight });
    };

    // Defer one frame so person cards have final layout
    const raf = requestAnimationFrame(measure);
    const ro = new ResizeObserver(measure);
    ro.observe(wrap);
    window.addEventListener("resize", measure);
    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [nodes, edges]);

  const details = (
    <>
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
    </>
  );

  return (
    <div className="pedigree-wrap">
      <div className="pedigree pedigree-hero" aria-label="Family tree by generation" ref={wrapRef}>
        <svg
          className="pedigree-lines"
          width={size.w || "100%"}
          height={size.h || "100%"}
          aria-hidden
        >
          {lines.map((ln, i) => (
            <line
              key={i}
              x1={ln.x1}
              y1={ln.y1}
              x2={ln.x2}
              y2={ln.y2}
              className={ln.kind === "sibling" ? "pedigree-line-sib" : "pedigree-line-pc"}
            />
          ))}
        </svg>
        {gens.map((g) => (
          <div key={g} className="generation-block">
            <div className="generation-label">Generation {g}</div>
            <div className="generation">
              {nodes
                .filter((n) => n.generation === g)
                .map((n) => {
                  const year = n.birth_year ?? birthYears?.[n.label];
                  return (
                    <div
                      className="person person-lg"
                      key={n.label}
                      ref={(el) => setNodeRef(n.label, el)}
                    >
                      <div className="role">{n.role}</div>
                      <div className="name">{n.label}</div>
                      <div className="muted">
                        {[n.sex, year != null ? `b. ${year}` : null].filter(Boolean).join(" · ") ||
                          "—"}
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        ))}
      </div>
      {pc.length + sibs.length > 0 && (
        <p className="muted pedigree-legend">
          Teal lines = parent → child · Coral braces = same-generation / sibling-range
        </p>
      )}

      {detailsCollapsed ? (
        <details className="about-collapse">
          <summary>Details (edges & ASCII)</summary>
          {details}
        </details>
      ) : (
        details
      )}
    </div>
  );
}
