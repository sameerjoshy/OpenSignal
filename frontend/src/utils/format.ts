export function formatNumber(value: number): string {
  if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
  return String(value);
}

export function formatCurrency(value: number): string {
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value >= 1000 ? 0 : 2,
  });
  return formatter.format(value);
}

export function formatCompactCurrency(value?: number | null): string {
  if (!value) return "—";
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  if (abs >= 1e12) return `${sign}$${(value / 1e12).toFixed(1)}T`;
  if (abs >= 1e9) return `${sign}$${(value / 1e9).toFixed(1)}B`;
  if (abs >= 1e6) {
    const v = value / 1e6;
    return `${sign}$${v >= 100 ? Math.round(v) : v.toFixed(1)}M`;
  }
  if (abs >= 1e3) return `${sign}$${(value / 1e3).toFixed(1)}k`;
  return `${sign}$${Math.round(value)}`;
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function timeAgo(value?: string | null): string {
  if (!value) return "—";
  const seconds = Math.floor((Date.now() - new Date(value).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function tierLabel(tier?: number | null): string {
  if (tier === 1) return "Tier 1";
  if (tier === 2) return "Tier 2";
  if (tier === 3) return "Tier 3";
  return "Unscored";
}

export function sourceLabel(source: string): string {
  const labels: Record<string, string> = {
    apollo: "Apollo",
    sec_edgar: "SEC EDGAR",
    newsapi: "NewsAPI",
    ga4: "GA4",
    manual: "Manual",
    hunter: "Hunter",
  };
  return labels[source] || source.replace(/_/g, " ");
}