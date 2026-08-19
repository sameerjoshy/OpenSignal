import { formatNumber } from "../utils/format";

interface MetricCardProps {
  label: string;
  value: number | string;
  delta?: string;
  icon?: string;
  accent?: "indigo" | "green" | "amber" | "blue" | "rose";
}

export default function MetricCard({ label, value, delta, icon, accent = "indigo" }: MetricCardProps) {
  const display = typeof value === "string" ? value : formatNumber(value);
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