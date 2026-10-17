type Hit = {
  rsid: string;
  gene?: string;
  category?: string;
  genotype?: string | null;
  note?: string;
  summary?: string;
  present?: boolean;
};

export function HitsTable({ hits }: { hits: Hit[] }) {
  return (
    <table className="data">
      <thead>
        <tr>
          <th>What this is</th>
          <th>Gene</th>
          <th>Your DNA</th>
          <th>What your result means</th>
        </tr>
      </thead>
      <tbody>
        {hits.map((h) => (
          <tr key={h.rsid} style={{ opacity: h.present === false ? 0.55 : 1 }}>
            <td>
              <div>{h.summary || h.rsid}</div>
              <div className="muted">{h.rsid}</div>
            </td>
            <td>{h.gene || "—"}</td>
            <td>{h.genotype || "Not called on this file"}</td>
            <td>{h.note || "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
