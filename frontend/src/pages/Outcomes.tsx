import { useEffect, useState } from "react";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import MetricCard from "../components/MetricCard";
import { formatCurrency } from "../utils/format";
import type { Outcomes } from "../types";

export default function OutcomesPage() {
  const [data, setData] = useState<Outcomes | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
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

  const maxTier = Math.max(...data.pipeline_by_tier.map((m) => m.value), 1);

  return (
    <div className="stack">
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

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Pipeline by tier</h2>
          </div>
          <div className="card-body">
            <div className="bar-chart">
              {data.pipeline_by_tier.map((tier) => (
                <div key={tier.label} className="bar-item" title={`${tier.label}: ${formatCurrency(tier.value)}`}>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ height: `${Math.max((tier.value / maxTier) * 100, 3)}%` }} />
                  </div>
                  <span className="bar-label">{tier.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Engagement vs. industry</h2>
          </div>
          <div className="card-body">
            <ul className="source-list">
              <li className="source-row">
                <span className="source-name">Reply rate</span>
                <span className="source-count">{data.reply_rate}% vs {data.industry_reply_rate}%</span>
              </li>
              <li className="source-row">
                <span className="source-name">Open rate</span>
                <span className="source-count">{data.open_rate}% vs {data.industry_reply_rate * 5.6}%*</span>
              </li>
              <li className="source-row">
                <span className="source-name">Click rate</span>
                <span className="source-count">{data.click_rate}%</span>
              </li>
              <li className="source-row">
                <span className="source-name">Engagement lift</span>
                <span className="source-count">{data.engagement_lift_pct}%</span>
              </li>
            </ul>
            <p className="muted-note">*Industry open-rate benchmark. Estimates from your activity and industry benchmarks.</p>
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