import { useEffect, useRef, useState } from "react";
import { formatNumber } from "../utils/format";

interface MetricCardProps {
  label: string;
  value: number | string;
  delta?: string;
  icon?: string;
  accent?: "indigo" | "green" | "amber" | "blue" | "rose";
}

/**
 * MetricCard with a count-up animation for numeric values.
 * String values (currencies, percents, "—") render instantly.
 */
export default function MetricCard({ label, value, delta, icon, accent = "indigo" }: MetricCardProps) {
  const [displayValue, setDisplayValue] = useState(() => (typeof value === "number" ? 0 : value));
  const previous = useRef(0);
  const raf = useRef<number>(0);

  useEffect(() => {
    if (typeof value !== "number") {
      setDisplayValue(value);
      return;
    }
    const from = previous.current;
    const to = value;
    previous.current = value;
    if (from === to) {
      setDisplayValue(to);
      return;
    }
    const start = performance.now();
    const duration = 700;
    cancelAnimationFrame(raf.current);
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.round(from + (to - from) * eased));
      if (progress < 1) {
        raf.current = requestAnimationFrame(tick);
      }
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [value]);

  const display = typeof displayValue === "string" ? displayValue : formatNumber(displayValue);

  return (
    <div className={`metric-card accent-${accent}`}>
      {icon && <span className="metric-icon">{icon}</span>}
      <div className="metric-body">
        <div className="metric-label">{label}</div>
        <div className="metric-value">{display}</div>
        {delta && <div className="metric-delta">{delta}</div>}
      </div>
    </div>
  );
}