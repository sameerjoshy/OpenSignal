import { useEffect, useState } from "react";
import { api } from "../lib/api";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";
import MetricCard from "../components/MetricCard";
import { BarChart } from "../components/charts";
import { useToast } from "../components/Toast";
import { formatCurrency } from "../utils/format";
import type { Outcomes } from "../types";

export default function OutcomesPage() {
  const [data, setData] = useState<Outcomes | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [sharing, setSharing] = useState(false);
  const { toast } = useToast();

  async function load() {
    setError(null);
    try {
      setData(await api.get<Outcomes>("/api/v1/analytics/outcomes"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load outcomes");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function exportCsv() {
    setExporting(true);
    try {
      await api.download("/api/v1/analytics/export.csv", "opensignal_outcomes.csv");
      toast("CSV exported", "success");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setExporting(false);
    }
  }

  async function shareLink() {
    setSharing(true);
    try {
      const result = await api.post<{ url: string; expires_at: string }>("/api/v1/analytics/share");
      const url = `${window.location.origin}${result.url}`;
      await navigator.clipboard.writeText(url);
      toast(`Share link copied (expires ${new Date(result.expires_at).toLocaleDateString()})`, "success");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setSharing(false);
    }
  }

  if (loading) {
    return <Skeleton variant="page" />;
  }

  if (error) {
    return (
      <div className="stack">
        <div className="alert alert-error">{error}</div>
      </div>
    );
  }

  if (!data) {
    return <EmptyState title="No outcomes yet" description="Score accounts and send campaigns to see value." />;
  }

  const tierColors: Record<string, string> = {
    "Tier 1": "var(--rose)",
    "Tier 2": "var(--amber)",
    "Tier 3": "var(--blue)",
  };

  const openBench = Math.round(data.industry_reply_rate * 5.6);

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">Outcomes</h1>
          <p className="page-desc">The business value Signal360 is driving — ROI, pipeline and time saved.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary btn-sm" onClick={shareLink} disabled={sharing} title="Copy a 7-day read-only link for stakeholders">
            {sharing ? "Sharing…" : "⧉ Share link"}
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => window.print()} title="Save as PDF via your browser print dialog">
            ⬇ Export PDF
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => void exportCsv()} disabled={exporting}>
            {exporting ? "Exporting…" : "⬇ Export CSV"}
          </button>
        </div>
      </div>

      <div className="metric-grid">
        <MetricCard label="Pipeline value" value={formatCurrency(data.pipeline_value)} icon="◉" accent="green" />
        <MetricCard label="Monthly forecast" value={formatCurrency(data.monthly_forecast)} icon="◍" accent="indigo" />
        <MetricCard label="Forecast growth" value={`${data.forecast_growth_pct}%`} icon="▲" accent="blue" />
        <MetricCard label="Deals (est.)" value={data.deals_estimate} icon="◈" accent="amber" />
      </div>

      <div className="metric-grid">
        <MetricCard label="Time saved" value={`${data.time_saved_hours}h`} icon="◷" accent="blue" />
        <MetricCard label="Labor value" value={formatCurrency(data.labor_value)} icon="◴" accent="green" />
        <MetricCard label="Cost per meeting" value={formatCurrency(data.cost_per_meeting)} icon="◒" accent="rose" />
        <MetricCard label="Accounts scored" value={data.accounts_scored} icon="◈" accent="indigo" />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Pipeline by tier</h2>
          <div className="card-sub">Estimated deal value weighted by account tier</div>
        </div>
        <div className="card-body">
          <BarChart
            data={data.pipeline_by_tier.map((t) => ({ label: t.label, value: t.value, color: tierColors[t.label] }))}
            money
            height={210}
          />
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Engagement vs. industry</h2>
            <div className="card-sub">Solid = you · dashed = benchmark</div>
          </div>
          <div className="card-body">
            <div className="cmp-row">
              <span className="cmp-label">Reply rate</span>
              <div className="cmp-track">
                <div className="cmp-bar" style={{ width: `${Math.min(data.reply_rate, 100)}%` }} />
                <div className="cmp-marker" style={{ left: `${Math.min(data.industry_reply_rate, 100)}%` }} />
              </div>
              <div className="cmp-val">
                <strong>{data.reply_rate}%</strong>
                <span className="muted"> vs {data.industry_reply_rate}%</span>
              </div>
            </div>
            <div className="cmp-row">
              <span className="cmp-label">Open rate</span>
              <div className="cmp-track">
                <div className="cmp-bar" style={{ width: `${Math.min(data.open_rate, 100)}%` }} />
                <div className="cmp-marker" style={{ left: `${Math.min(openBench, 100)}%` }} />
              </div>
              <div className="cmp-val">
                <strong>{data.open_rate}%</strong>
                <span className="muted"> vs {openBench}%*</span>
              </div>
            </div>
            <div className="cmp-row">
              <span className="cmp-label">Click rate</span>
              <div className="cmp-track">
                <div className="cmp-bar" style={{ width: `${Math.min(data.click_rate, 100)}%` }} />
                <div className="cmp-bar alt" style={{ width: `${Math.min(data.industry_reply_rate * 3, 100)}%` }} />
              </div>
              <div className="cmp-val">
                <strong>{data.click_rate}%</strong>
                <span className="muted"> vs {Math.round(data.industry_reply_rate * 3)}%*</span>
              </div>
            </div>
            <div className="cmp-row">
              <span className="cmp-label">Engagement lift</span>
              <div className="cmp-track">
                <div className="cmp-bar" style={{ width: `${Math.min(data.engagement_lift_pct, 100)}%` }} />
              </div>
              <div className="cmp-val">
                <strong>{data.engagement_lift_pct}%</strong>
              </div>
            </div>
            <p className="muted-note">*Industry benchmarks. Estimates from your activity and industry averages.</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Pipeline detail</h2>
          </div>
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th className="num">Weight</th>
                  <th className="num">Pipeline</th>
                </tr>
              </thead>
              <tbody>
                {data.pipeline_by_tier.map((tier) => (
                  <tr key={tier.label}>
                    <td>{tier.label}</td>
                    <td className="num">{tier.value}</td>
                    <td className="num">
                      <strong>{formatCurrency((data.pipeline_value * tier.value) / (data.pipeline_by_tier.reduce((s, t) => s + t.value, 0) || 1))}</strong>
                    </td>
                  </tr>
                ))}
                <tr>
                  <td>
                    <strong>Total</strong>
                  </td>
                  <td className="num">
                    <strong>{data.pipeline_by_tier.reduce((s, t) => s + t.value, 0)}</strong>
                  </td>
                  <td className="num">
                    <strong>{formatCurrency(data.pipeline_value)}</strong>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">What this means</h2>
        </div>
        <div className="card-body">
          <p className="muted-note">{data.note}</p>
        </div>
      </div>
    </div>
  );
}