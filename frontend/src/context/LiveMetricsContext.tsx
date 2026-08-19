import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { API_BASE } from "../config";
import { getToken } from "../lib/api";
import { useAuth } from "./AuthContext";
import type { LiveEvent } from "../types";

interface LiveMetricsValue {
  events: LiveEvent[];
  connected: boolean;
}

const LiveMetricsContext = createContext<LiveMetricsValue>({ events: [], connected: false });

function wsUrl(token: string): string {
  const base = API_BASE || window.location.origin;
  return base.replace(/^http/, "ws") + "/ws/metrics?token=" + encodeURIComponent(token);
}

/**
 * Single app-wide WebSocket to /ws/metrics (authenticated per-user). Safe no-op
 * when there is no session or the connection cannot be established.
 */
export function LiveMetricsProvider({ children, maxEvents = 30 }: { children: React.ReactNode; maxEvents?: number }) {
  const { user } = useAuth();
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const maxEventsRef = useRef(maxEvents);
  maxEventsRef.current = maxEvents;

  useEffect(() => {
    if (!user) return;

    let ws: WebSocket | null = null;
    let closed = false;
    let retryTimer: number | undefined;
    let retries = 0;

    setEvents([]);
    setConnected(false);

    const connect = () => {
      if (closed) return;
      const token = getToken();
      if (!token) return;
      try {
        ws = new WebSocket(wsUrl(token));
      } catch {
        return;
      }
      ws.onopen = () => {
        retries = 0;
        setConnected(true);
      };
      ws.onmessage = (msg) => {
        try {
          const parsed = JSON.parse(msg.data as string) as LiveEvent;
          if (parsed && parsed.type) {
            setEvents((prev) => [...prev.slice(-(maxEventsRef.current - 1)), parsed]);
          }
        } catch {
          // ignore malformed frames
        }
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed) {
          retries += 1;
          retryTimer = window.setTimeout(connect, Math.min(15000, 1000 * retries));
        }
      };
      ws.onerror = () => {
        ws?.close();
      };
    };

    connect();
    return () => {
      closed = true;
      if (retryTimer) window.clearTimeout(retryTimer);
      ws?.close();
    };
  }, [user]);

  return <LiveMetricsContext.Provider value={{ events, connected }}>{children}</LiveMetricsContext.Provider>;
}

export function useLiveMetrics(): LiveMetricsValue {
  return useContext(LiveMetricsContext);
}