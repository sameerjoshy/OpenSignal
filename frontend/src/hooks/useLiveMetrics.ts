import { useEffect, useRef, useState } from "react";
import { API_BASE } from "../config";
import type { LiveEvent } from "../types";

function wsUrl(): string {
  const base = API_BASE || window.location.origin;
  return base.replace(/^http/, "ws") + "/ws/metrics";
}

/**
 * Opens a WebSocket to /ws/metrics and collects live events (email_sent,
 * email_event, account_scored, campaign_run, reply_classified).
 * Safe no-op when the connection cannot be established (backend offline, ws blocked).
 */
export function useLiveMetrics(maxEvents = 30) {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const retryRef = useRef<number>(0);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let closed = false;
    let retryTimer: number | undefined;

    const connect = () => {
      if (closed) return;
      try {
        ws = new WebSocket(wsUrl());
      } catch {
        return;
      }
      ws.onopen = () => {
        retryRef.current = 0;
        setConnected(true);
      };
      ws.onmessage = (msg) => {
        try {
          const parsed = JSON.parse(msg.data as string) as LiveEvent;
          if (parsed && parsed.type) {
            setEvents((prev) => [...prev.slice(-(maxEvents - 1)), parsed]);
          }
        } catch {
          // ignore malformed frames
        }
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed) {
          retryRef.current += 1;
          retryTimer = window.setTimeout(connect, Math.min(15000, 1000 * retryRef.current));
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
  }, [maxEvents]);

  return { events, connected };
}