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
          <th>rsID</th>
          <th>Gene</th>
          <th>Genotype</th>
          <th>Note</th>
        </tr>
      </thead>
      <tbody>
        {hits.map((h) => (
          <tr key={h.rsid} style={{ opacity: h.present === false ? 0.55 : 1 }}>
            <td>{h.rsid}</td>
            <td>{h.gene || ""}</td>
            <td>{h.genotype || "—"}</td>
            <td>
              <div>{h.note}</div>
              {h.summary ? <div className="muted">{h.summary}</div> : null}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
