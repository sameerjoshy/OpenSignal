import { useAnalytics } from "../hooks/useAnalytics";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import MetricCard from "../components/MetricCard";

export default function Analytics() {
  const { data, loading, error, refresh } = useAnalytics();

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
    return <EmptyState title="No analytics yet" description="Send your first campaign to see performance." />;
  }

  const maxWeekly = Math.max(...data.weekly_activity.map((m) => m.value), 1);
  const maxFunnel = Math.max(...data.funnel.map((f) => f.value), 1);

  return (
    <div className="stack">
      <div className="metric-grid">
        <MetricCard label="Total signals" value={data.total_signals} icon="◎" accent="indigo" />
        <MetricCard label="Signals this week" value={data.signals_this_week} icon="◆" accent="blue" />
        <MetricCard label="Total accounts" value={data.total_accounts} icon="◈" accent="amber" />
        <MetricCard label="Campaigns" value={data.total_campaigns} icon="◉" accent="green" />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Signals by source</h2>
          <button className="btn btn-ghost btn-sm" onClick={refresh}>
            Refresh
          </button>
        </div>
        <div className="card-body">
          <ul className="source-list">
            {data.top_sources.map((source) => (
              <li key={source.label} className="source-row">
                <span className="source-name">{source.label}</span>
                <span className="source-count">{source.value}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Weekly activity</h2>
        </div>
        <div className="card-body">
          <div className="bar-chart">
            {data.weekly_activity.map((point) => (
              <div key={point.label} className="bar-item" title={`${point.label}: ${point.value}`}>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ height: `${Math.max((point.value / maxWeekly) * 100, 3)}%` }}
                  />
                </div>
                <span className="bar-label">{point.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Engagement funnel</h2>
          </div>
          <div className="card-body">
            <div className="funnel">
              {data.funnel.map((step) => (
                <div key={step.label} className="funnel-step">
                  <div className="funnel-label">{step.label}</div>
                  <div className="funnel-track">
                    <div className="funnel-bar" style={{ width: `${(step.value / maxFunnel) * 100}%` }} />
                  </div>
                  <div className="funnel-value">{step.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Signals by tier</h2>
          </div>
          <div className="card-body">
            <ul className="source-list">
              {data.signals_by_tier.map((tier) => (
                <li key={tier.label} className="source-row">
                  <span className="source-name">{tier.label}</span>
                  <span className="source-count">{tier.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}