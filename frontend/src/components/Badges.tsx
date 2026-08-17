import { tierLabel } from "../utils/format";

export function TierBadge({ tier }: { tier?: number | null }) {
  if (!tier) {
    return <span className="badge badge-muted">{tierLabel(null)}</span>;
  }
  return <span className={`badge badge-tier${tier}`}>{tierLabel(tier)}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const className = `badge badge-status badge-${status}`;
  return <span className={className}>{status}</span>;
}

export function SourceBadge({ source }: { source: string }) {
  return <span className={`badge badge-source source-${source}`}>{source.replace(/_/g, " ")}</span>;
}

export function SignalTypeBadge({ type }: { type: string }) {
  return <span className={`badge badge-type type-${type}`}>{type.replace(/_/g, " ")}</span>;
}