import { useAnalytics } from "../hooks/useAnalytics";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";
import MetricCard from "../components/MetricCard";
import { AreaChart, BarChart, DonutChart, FunnelBars, MiniBars } from "../components/charts";

export default function Analytics() {
  const { data, loading, error, refresh } = useAnalytics();

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
    return <EmptyState title="No analytics yet" description="Send your first campaign to see performance." />;
  }

  const funnel = data.funnel.map((f) => ({ label: f.label, value: f.value }));
  const tierColors: Record<string, string> = {
    "Tier 1": "var(--rose)",
    "Tier 2": "var(--amber)",
    "Tier 3": "var(--blue)",
  };

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="page-desc">Activity, engagement and conversion across your signal intelligence pipeline.</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary btn-sm" onClick={refresh}>
            ⟳ Refresh
          </button>
        </div>
      </div>

      <div className="metric-grid">
        <MetricCard label="Total signals" value={data.total_signals} icon="◎" accent="indigo" />
        <MetricCard label="Signals this week" value={data.signals_this_week} icon="◆" accent="blue" />
        <MetricCard label="Total accounts" value={data.total_accounts} icon="◈" accent="amber" />
        <MetricCard label="Campaigns" value={data.total_campaigns} icon="◉" accent="green" />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Weekly activity</h2>
          <div className="card-sub">Signals captured per week — hover for exact values</div>
        </div>
        <div className="card-body">
          <AreaChart data={data.weekly_activity} />
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Signals by source</h2>
          </div>
          <div className="card-body">
            <MiniBars data={data.top_sources} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Signals by tier</h2>
          </div>
          <div className="card-body">
            <DonutChart
              data={data.signals_by_tier.map((t) => ({ label: t.label, value: t.value, color: tierColors[t.label] }))}
              centerValue={String(data.total_signals)}
              centerLabel="signals"
            />
          </div>
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Engagement funnel</h2>
            <div className="card-sub">Conversion rate vs. the previous stage</div>
          </div>
          <div className="card-body">
            <FunnelBars data={funnel} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Signals by day (this week)</h2>
          </div>
          <div className="card-body">
            <BarChart
              data={data.weekly_activity.slice(-7).map((m) => ({ label: m.label, value: m.value }))}
              height={200}
            />
          </div>
        </div>
      </div>
    </div>
  );
}