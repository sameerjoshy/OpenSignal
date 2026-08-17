import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import type { Signal } from "../types";

export interface SignalFilters {
  source?: string;
  signal_type?: string;
  tier?: number;
}

export function useSignals(filters: SignalFilters = {}) {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.source) params.set("source", filters.source);
      if (filters.signal_type) params.set("signal_type", filters.signal_type);
      if (filters.tier) params.set("tier", String(filters.tier));
      const query = params.toString();
      const result = await api.get<Signal[]>(`/api/v1/signals${query ? `?${query}` : ""}`);
      setSignals(result);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [filters.source, filters.signal_type, filters.tier]);

  useEffect(() => {
    void load();
  }, [load]);

  return { signals, loading, error, refresh: load };
}