import { useCallback, useEffect, useRef, useState } from "react";
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
  const controllerRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.source) params.set("source", filters.source);
      if (filters.signal_type) params.set("signal_type", filters.signal_type);
      if (filters.tier) params.set("tier", String(filters.tier));
      const query = params.toString();
      const result = await api.get<Signal[]>(`/api/v1/signals${query ? `?${query}` : ""}`, {
        signal: controller.signal,
      });
      setSignals(result);
      setError(null);
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [filters.source, filters.signal_type, filters.tier]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => () => controllerRef.current?.abort(), []);

  return { signals, loading, error, refresh: load };
}