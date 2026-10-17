"use client";

import { useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { putMeta } from "@/lib/api";
import { useSample } from "@/lib/sample";

export default function SamplesSettingsPage() {
  const { samples, refresh } = useSample();
  const [drafts, setDrafts] = useState<Record<string, { birth_year?: string; generation?: string }>>({});
  const [msg, setMsg] = useState("");

  const save = async (id: string) => {
    const d = drafts[id] || {};
    await putMeta(id, {
      birth_year: d.birth_year ? Number(d.birth_year) : null,
      generation: d.generation || null,
    });
    setMsg(`Saved metadata for ${id}`);
    refresh();
  };

  return (
    <div className="panel">
      <h1>Samples & ages</h1>
      <Disclaimer text="Birth year / generation are stored in gitignored data/sample_meta.json and help orient the family tree." />
      {msg && <p className="muted">{msg}</p>}
      <table className="data">
        <thead>
          <tr>
            <th>Sample</th>
            <th>Birth year</th>
            <th>Generation</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {samples.map((s) => {
            const meta = (s.meta || {}) as Record<string, unknown>;
            const draft = drafts[s.id] || {
              birth_year: meta.birth_year != null ? String(meta.birth_year) : "",
              generation: (meta.generation as string) || "",
            };
            return (
              <tr key={s.id}>
                <td>{s.label}</td>
                <td>
                  <input
                    value={draft.birth_year || ""}
                    placeholder="e.g. 1950"
                    onChange={(e) =>
                      setDrafts((prev) => ({
                        ...prev,
                        [s.id]: { ...draft, birth_year: e.target.value },
                      }))
                    }
                  />
                </td>
                <td>
                  <select
                    value={draft.generation || ""}
                    onChange={(e) =>
                      setDrafts((prev) => ({
                        ...prev,
                        [s.id]: { ...draft, generation: e.target.value },
                      }))
                    }
                  >
                    <option value="">—</option>
                    <option value="grandparent">Grandparent</option>
                    <option value="parent">Parent</option>
                    <option value="self">Self</option>
                    <option value="child">Child</option>
                  </select>
                </td>
                <td>
                  <button className="cta secondary" onClick={() => save(s.id)}>
                    Save
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
