"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getSamples, type Sample } from "./api";

type Ctx = {
  samples: Sample[];
  primaryId: string;
  setPrimaryId: (id: string) => void;
  loading: boolean;
  error: string | null;
  refresh: () => void;
};

const SampleContext = createContext<Ctx | null>(null);

export function SampleProvider({ children }: { children: React.ReactNode }) {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [primaryId, setPrimaryId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    setLoading(true);
    getSamples()
      .then((data) => {
        setSamples(data.samples);
        setPrimaryId((prev) => prev || data.default_primary_id || data.samples[0]?.id || "");
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
  }, []);

  const value = useMemo(
    () => ({ samples, primaryId, setPrimaryId, loading, error, refresh }),
    [samples, primaryId, loading, error]
  );

  return <SampleContext.Provider value={value}>{children}</SampleContext.Provider>;
}

export function useSample() {
  const ctx = useContext(SampleContext);
  if (!ctx) throw new Error("useSample requires SampleProvider");
  return ctx;
}
